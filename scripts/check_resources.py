"""Local T07 measurements: one run, one/two views, idle/pause and response."""
from dataclasses import replace
import json
import os
from pathlib import Path
import resource
import time
import torch
from PySide6.QtWidgets import QApplication
from wave_studio.ui.editor import MainWindow
from wave_studio.domain.project import Project,SimulationSettings,SourceObject,DetectorObject

torch.set_num_threads(1)
os.environ['WAVESTUDIO_RECOVERY_DIR']='/tmp/wave-studio-resources-recovery'
app=QApplication([]);w=MainWindow();w.show()
report={'machine':'Apple M1 / 8 GiB','grid':[512,512],'cpu_threads':1,'memory_note':'RSS peak is process-wide. MPS allocation is reported separately, never added to unified-memory RSS. GPU utilization was not sampled.'}

def observe(seconds):
    start=time.monotonic();cpu=time.process_time();frames=0;last=-1;first=w.frame.steps if w.frame else 0
    while time.monotonic()-start<seconds:
        app.processEvents()
        if w.frame and w.frame.steps!=last:frames+=1;last=w.frame.steps
        time.sleep(.001)
    elapsed=time.monotonic()-start
    return {'process_cpu_seconds_per_second':(time.process_time()-cpu)/elapsed,'displayed_frames_per_second':frames/elapsed,'steps_per_second':((w.frame.steps if w.frame else 0)-first)/elapsed,'rss_peak_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}

try:
    for backend in ('cpu','mps'):
        if backend=='mps' and not torch.backends.mps.is_available():continue
        p=Project(settings=SimulationSettings(64,64,.125,.5,6,2,backend),objects=(SourceObject(start=(32,32),wavelength=4),),detectors=(DetectorObject(start=(48,20),end=(48,44),samples=161,settling=10,window=20),))
        w.replace_project(p);idle=observe(.4)
        w.run_simulation();observe(.3);one=observe(1)
        w.secondary_action.setChecked(True);observe(.2);two=observe(1)
        begin=time.monotonic();w.pause_simulation()
        while w.frame is None or not w.frame.paused:
            app.processEvents();time.sleep(.001)
            if time.monotonic()-begin>2:raise AssertionError('Pause timed out')
        latency=(time.monotonic()-begin)*1000
        paused=observe(.4)
        data={'idle':idle,'one_view_economical':one,'two_views_economical':two,'pause_latency_ms':latency,'paused':paused}
        w.run_simulation();w.mode_combo.setCurrentText('Performance');observe(.2);data['two_views_performance']=observe(.5)
        w.pause_simulation();observe(.1)
        if backend=='mps':data['mps_allocated_bytes']=torch.mps.current_allocated_memory()
        report[backend]=data
finally:
    w.lifecycle.dirty=False;w.close();app.processEvents()
Path('docs/resource-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2))
