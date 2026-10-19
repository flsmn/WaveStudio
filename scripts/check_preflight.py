"""Record selected grids and measure homogeneous frequencies on local modal patches."""
from dataclasses import asdict,replace
from pathlib import Path
import json,math
import numpy as np
import torch
from wave_sim2d.config import Grid,Material,rectangle
from wave_sim2d.geometry import prepare_scene
from wave_sim2d.wave_simulation import WaveSimulator2D
from wave_sim2d.dispersion import temporal_frequency
from wave_studio.domain.project import *
from wave_studio.domain.quality import estimate,measures,PRESETS
from wave_studio.examples import example

torch.set_num_threads(1)
a=.51;c,s=math.cos(a),math.sin(a)
vertices=tuple((30+x*c-y*s,8+x*s+y*c) for x,y in ((-3,-.1),(3,-.1),(3,.1),(-3,.1)))
long=Project(settings=SimulationSettings(width=136,height=16,border_width=2),objects=(SourceObject(start=(4,8),wavelength=2),MaterialObject(vertices=vertices),WallObject(x=60,y=5,width=.3,height=6)),detectors=(DetectorObject(start=(132,8),end=None,samples=1),))
report={'method':'Homogeneous finite-domain sine eigenmodes on local patches at the actual selected dx/dt; long-path phase is a Fourier-symbol estimate, not a full-domain propagated measurement.','cases':[]}
for name,p in [('64-wavelength rotated-thin-structure',long),('Refraction',example('Refraction')),('Biconvex lens',example('Biconvex lens'))]:
 wavelength,index,feature,path=measures(p)
 for preset in PRESETS:
  e=estimate(p,preset);r={'scene':name,'preset':asdict(e),'modes':[]}
  if not e.supported:r['status']='resource-rejected';report['cases'].append(r);continue
  # About eight material wavelengths; exact zero boundaries at q=0,L.
  cells=max(32,round(8*wavelength/(index*e.dx)));length=cells*e.dx
  g=Grid(cells+1,cells+1,e.dx,p.settings.courant*e.dx,0,0);q=np.arange(g.nx)*g.dx
  for mx,my in ((16,2),(12,12)):
   kx,ky=mx*math.pi/length,my*math.pi/length
   u=(np.sin(kx*q)[None,:]*np.sin(ky*q)[:,None]).astype('float32')
   sim=WaveSimulator2D.from_scene(prepare_scene(g,[Material(rectangle(0,0,g.width,g.height),index)]),device='cpu',initial_field=u)
   history=[]
   for _ in range(180):
    sim.step();history.append(float(np.sum(sim.snapshot()*u,dtype=np.float64)))
   v=np.asarray(history);cosine=np.dot(v[1:-1],v[:-2]+v[2:])/(2*np.dot(v[1:-1],v[1:-1]));actual=math.acos(float(cosine))/g.dt;predicted=temporal_frequency(kx,ky,g.dx,g.dt,index)
   r['modes'].append({'mode':[mx,my],'measured_frequency':actual,'predicted_frequency':predicted,'prediction_relative_error':abs(actual/predicted-1),'speed_relative_error':abs(actual/(math.hypot(kx,ky)/index)-1)})
  r['status']='passed' if all(v['prediction_relative_error']<=.001 and v['speed_relative_error']<=.02 for v in r['modes']) else 'failed'
  report['cases'].append(r)
report['passed']=all(r['status']!='failed' for r in report['cases'])
output=Path('local-results/quality-preflight-results.json');output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));raise SystemExit(0 if report['passed'] else 1)
