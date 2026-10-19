"""Additional Mac preset probes; criteria frozen in MAC_ACCEPTANCE_PLAN.md."""
from dataclasses import asdict,replace
import argparse,gc,json,math,time,platform
from pathlib import Path
import numpy as np
import torch
from wave_studio.examples import example
from wave_studio.domain.quality import estimate,PRESETS
from wave_studio.simulation.compiler import compile_project
from wave_sim2d.geometry import prepare_scene
from wave_sim2d.wave_simulation import WaveSimulator2D


def load_mac_limits(path):
    """Read the shared, unchanged v1 policy instead of duplicating thresholds."""
    profile=json.loads(path.read_text())
    limits=json.loads((path.parent/profile['extends']).read_text())
    for name,values in profile['overrides'].items():
        limits[name].update(values)
    return limits


def demodulate(scene,positions,settle,window,device):
    sim=WaveSimulator2D.from_scene(scene,device=device)
    xy=positions/scene.grid.dx-.5;base=np.floor(xy).astype(int);frac=xy-base
    indices=[];weights=[]
    for dy in (0,1):
        for dx in (0,1):
            indices.append(torch.tensor((base[:,1]+dy)*scene.grid.nx+base[:,0]+dx,device=device))
            weights.append(torch.tensor((frac[:,0] if dx else 1-frac[:,0])*(frac[:,1] if dy else 1-frac[:,1]),device=device,dtype=torch.float32))
    remaining=math.ceil(settle/sim.dt)
    while remaining:
        count=min(128,remaining);sim.step(count);remaining-=count
    omega=scene.sources[0].omega;real=torch.zeros(len(positions),device=device);imag=torch.zeros_like(real);count=0
    stop=sim.t+window
    # At least 14 observations per cycle on every selected grid; no full-field CPU transfers.
    stride=min(4,max(1,int((2*math.pi/omega)/(16*sim.dt))))
    while sim.t<stop:
        sim.step(stride);values=sum(sim.u.view(-1)[i]*w for i,w in zip(indices,weights))
        real.add_(values,alpha=math.cos(omega*sim.t));imag.add_(values,alpha=-math.sin(omega*sim.t));count+=1
    z=(real.cpu().numpy()+1j*imag.cpu().numpy())*2/count
    wall=float(sim.u[sim.walls].abs().max().item())
    del sim;gc.collect()
    if device=='mps':torch.mps.empty_cache()
    return z,wall


def main():
    ap=argparse.ArgumentParser();ap.add_argument('--case',choices=['slit','lens'],required=True);ap.add_argument('--device',default='mps')
    ap.add_argument('--policy',type=Path,default=Path(__file__).resolve().parents[2]/'WaveSimulator2D/validation/mac-presets-v1.json')
    args=ap.parse_args();limits=load_mac_limits(args.policy)
    torch.set_num_threads(1)
    output=Path('local-results/quality-'+args.case+'-results.json');output.parent.mkdir(parents=True,exist_ok=True)
    project=example('Double slit' if args.case=='slit' else 'Biconvex lens')
    report={'platform':platform.platform(),'device':args.device,'cases':[],'presets':[asdict(estimate(project,n)) for n in PRESETS],'tolerances':limits,'acceptance_scope':'historical v1 demonstration; no quantitative certification'}
    def save():output.write_text(json.dumps(report,indent=2,allow_nan=False)+'\n')
    save()
    choices=[(n,estimate(project,n).dx) for n in PRESETS if estimate(project,n).supported]
    # Balanced/High lens are above the frozen resource guard. Compare Preview with
    # the adjacent affordable custom grid, retaining exactly the same geometry.
    if args.case=='lens':choices.append(('Custom convergence',.025))
    for name,dx in choices:
        began=time.monotonic();print(f'{args.case}: {name} dx={dx}',flush=True)
        p=replace(project,settings=replace(project.settings,dx=dx,quality=name if name in PRESETS else 'Custom'))
        scene=compile_project(p)
        if args.case=='slit':
            yy=np.linspace(24,40,257);pos=np.column_stack((np.full_like(yy,52),yy));z,wall=demodulate(scene,pos,60,24,args.device)
            power=abs(z)**2;middle=len(yy)//2
            minima=[i for i in range(middle+2,len(yy)-1) if power[i]<power[i-1] and power[i]<power[i+1]]
            measured=float(yy[minima[0]]-32) if minima else None
            offsets=np.linspace(.01,10,10001);difference=np.sqrt(22**2+(offsets+3)**2)-np.sqrt(22**2+(offsets-3)**2);ref=float(offsets[np.argmin(abs(difference-1))])
            error=abs(measured/ref-1) if measured is not None else 1e9;asym=float(np.max(abs(power-power[::-1]))/power.max())
            bound=limits['T03']
            r={'name':name,'dx':dx,'grid':[scene.grid.nx,scene.grid.ny],'first_minimum':measured,'reference':ref,'relative_error':error,'asymmetry':asym,'wall_max':wall,'passed':error<=bound['first_minimum_position_relative_error'] and asym<=bound['symmetry_relative_error'] and wall<=bound['wall_field_max']}
        else:
            n=1.5;radius=24;aperture=16;thickness=2*(radius-math.sqrt(radius**2-(aperture/2)**2));f=1/((n-1)*(2/radius-(n-1)*thickness/(n*radius**2)));bfl=f*(1-(n-1)*thickness/(n*radius));rear=30+thickness/2
            xx=np.linspace(rear+.6*bfl,rear+1.4*bfl,321);pos=np.column_stack((xx,np.full_like(xx,24)))
            z,_=demodulate(scene,pos,80,16,args.device);print('lens: background',flush=True)
            background=prepare_scene(scene.grid,sources=[])
            # Reuse the exact prepared illumination to avoid changing source quadrature.
            background=replace(background,sources=scene.sources)
            base,_=demodulate(background,pos,80,16,args.device)
            power=abs(z)**2;peak=int(np.argmax(power));distance=float(xx[peak]-rear);error=abs(distance/bfl-1);gain=float(power[peak]/abs(base[peak])**2)
            bound=limits['T04']
            r={'name':name,'dx':dx,'grid':[scene.grid.nx,scene.grid.ny],'focus_x':float(xx[peak]),'back_focal_reference':bfl,'relative_error':error,'gain':gain,'passed':error<=bound['focus_position_relative_error'] and gain>=bound['minimum_focus_gain']}
        r['seconds']=time.monotonic()-began;report['cases'].append(r);save();print(json.dumps(r),flush=True)
    if args.case=='lens':
        report['focus_shift']=abs(report['cases'][0]['focus_x']-report['cases'][1]['focus_x'])/bfl
    report['passed']=all(r['passed'] for r in report['cases']) and report.get('focus_shift',0)<=limits['T04']['grid_focus_shift_relative_error'];save()
    return 0 if report['passed'] else 1

if __name__=='__main__':raise SystemExit(main())
