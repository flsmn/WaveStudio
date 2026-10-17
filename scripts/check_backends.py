"""T08 short backend comparison, plus provisional 512-square compute metrics."""
import json
from pathlib import Path
import platform
import resource
import time
import numpy as np
import torch
from wave_sim2d.config import Grid,Source,Material,Wall,rectangle
from wave_sim2d.geometry import prepare_scene
from wave_sim2d.wave_simulation import WaveSimulator2D

torch.set_num_threads(1)
report={'platform':platform.platform(),'torch':torch.__version__,'cpu_threads':1,'comparison_tolerances':{'relative_l2':.005,'max_absolute':.0005},'backends':{}}
grid=Grid(128,128,.25,.125,4)
scene=prepare_scene(grid,[Material(rectangle(19,8,5,16),1.5,.1)],walls=[Wall(26,0,.5,12)],sources=[Source((12,16),wavelength=4),Source((9,8),(9,24),wavelength=4,amplitude=.1)])
reference=None
for backend in ('cpu','mps'):
    if backend=='mps' and not torch.backends.mps.is_available():
        report['backends'][backend]={'available':False}
        continue
    sim=WaveSimulator2D.from_scene(scene,device=backend)
    sim.step(180)
    values=sim.snapshot()
    if reference is None: reference=values
    l2=float(np.linalg.norm(values-reference)/np.linalg.norm(reference))
    maximum=float(abs(values-reference).max())
    big=WaveSimulator2D.from_scene(prepare_scene(Grid(512,512,.125,.0625,6),sources=[Source((32,32),wavelength=4)]),device=backend)
    big.step(8)
    if backend=='mps': torch.mps.synchronize()
    begin=time.monotonic(); cpu_begin=time.process_time()
    big.step(100)
    if backend=='mps': torch.mps.synchronize()
    elapsed=time.monotonic()-begin
    cpu_elapsed=time.process_time()-cpu_begin
    report['backends'][backend]={'available':True,'relative_l2':l2,'max_absolute':maximum,'passed':l2<=.005 and maximum<=.0005,'steps_per_second_512':100/elapsed,'mean_step_ms_512':elapsed*10,'process_cpu_seconds_per_wall_second':cpu_elapsed/elapsed,'rss_peak_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    if backend=='mps':
        report['backends'][backend]['mps_allocated_bytes']=torch.mps.current_allocated_memory()
        report['backends'][backend]['memory_note']='Unified memory: MPS allocation is reported separately and must not be added to RSS.'
Path('docs/backend-results.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
raise SystemExit(0 if all(b.get('passed',True) for b in report['backends'].values()) else 1)
