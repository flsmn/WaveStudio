"""Bounded-command response on the affordable lens Preview grid; not a 20-fps claim."""
from dataclasses import replace
import json,os,time,resource
from pathlib import Path
import torch
from PySide6.QtWidgets import QApplication
from wave_studio.ui.editor import MainWindow
from wave_studio.examples import example
from wave_studio.domain.quality import estimate

torch.set_num_threads(1);os.environ['WAVESTUDIO_RECOVERY_DIR']='/tmp/wave-mac-large-recovery'
app=QApplication([]);app.setStyle('Fusion');w=MainWindow();w.show()
p=example('Biconvex lens');e=estimate(p,'Preview');p=replace(p,settings=replace(p.settings,dx=e.dx,quality='Preview',device='mps'))
r={'grid':[e.nx,e.ny],'estimated_buffer_bytes':e.estimated_bytes,'block_steps':1,'note':'Large-grid response observation. The 20-fps/1-GiB reference budgets apply to 512² only.'}
try:
 w.replace_project(p);w.run_simulation();deadline=time.monotonic()+20
 while not w.frame or w.frame.steps<4:
  app.processEvents();time.sleep(.001)
  if time.monotonic()>deadline:raise AssertionError(w.message.text())
 start=time.monotonic();w.pause_simulation()
 while not w.frame.paused:
  app.processEvents();time.sleep(.001)
  if time.monotonic()-start>2:raise AssertionError('Large grid pause exceeded two seconds')
 r['pause_ms']=(time.monotonic()-start)*1000;r['steps_at_pause']=w.frame.steps;r['rss_peak_bytes']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
 start=time.monotonic()
 while time.monotonic()-start<.4:app.processEvents();time.sleep(.002)
 r['paused_steps_stable']=w.frame.steps==r['steps_at_pause'];r['passed']=r['paused_steps_stable']
finally:w.lifecycle.dirty=False;w.close();app.processEvents()
Path('docs/large-grid-results.json').write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
