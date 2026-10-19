"""Local T07 measurements: one run, one/two views, idle/pause and response."""
from dataclasses import replace
import json
import os
from pathlib import Path
import resource
import plistlib,subprocess
import time
import torch
from PySide6.QtWidgets import QApplication
from wave_studio.ui.editor import MainWindow
from wave_studio.domain.project import Project,SimulationSettings,SourceObject,DetectorObject

torch.set_num_threads(1)
os.environ['WAVESTUDIO_RECOVERY_DIR']='/tmp/wave-studio-resources-recovery'
app=QApplication([]);app.setStyle('Fusion');w=MainWindow();w.show()
report={'machine':'Apple M1 / 8 GiB','grid':[512,512],'cpu_threads':1,'memory_note':'RSS peak is process-wide. MPS allocation is reported separately, never added to unified-memory RSS. GPU counters are system-wide IORegistry samples, including other apps and the window compositor; no calibrated process energy attribution.'}

def gpu():
    try:
        items=plistlib.loads(subprocess.check_output(['/usr/sbin/ioreg','-r','-c','AGXAccelerator','-a'],stderr=subprocess.DEVNULL))
        stats=items[0].get('PerformanceStatistics',{})
        return {k:stats[k] for k in ('Device Utilization %','Renderer Utilization %','Tiler Utilization %') if k in stats}
    except Exception as error:return {'unavailable':str(error)}

def observe(seconds):
    start=time.monotonic();cpu=time.process_time();frames=0;last=w.frame.steps if w.frame else -1;first=w.frame.steps if w.frame else 0
    while time.monotonic()-start<seconds:
        app.processEvents()
        if w.frame and w.frame.steps!=last:frames+=1;last=w.frame.steps
        time.sleep(.001)
    elapsed=time.monotonic()-start
    return {'process_cpu_seconds_per_second':(time.process_time()-cpu)/elapsed,'displayed_frames_per_second':frames/elapsed,'steps_per_second':((w.frame.steps if w.frame else 0)-first)/elapsed,'rss_peak_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'gpu_system_sample':gpu()}

try:
    for backend in ('cpu','mps'):
        if backend=='mps' and not torch.backends.mps.is_available():continue
        p=Project(settings=SimulationSettings(64,64,.125,.5,6,2,backend),objects=(SourceObject(start=(32,32),wavelength=4),),detectors=(DetectorObject(start=(48,20),end=(48,44),samples=161,settling=10,window=20),))
        w.replace_project(p);observe(.7);idle=observe(.8)
        w.run_simulation();observe(.7);one=observe(3)
        w.secondary_action.setChecked(True);observe(.4);two=observe(3)
        begin=time.monotonic();w.pause_simulation()
        while w.frame is None or not w.frame.paused:
            app.processEvents();time.sleep(.001)
            if time.monotonic()-begin>2:raise AssertionError('Pause timed out')
        latency=(time.monotonic()-begin)*1000
        observe(.15);paused=observe(.8)
        pauses=[latency]
        for _ in range(4):
            previous=w.frame.steps;w.run_simulation();observe(.25)
            if w.frame.paused or w.frame.steps<=previous:raise AssertionError('Resume did not advance before repeated pause')
            begin=time.monotonic();w.pause_simulation()
            while w.frame is None or not w.frame.paused:
                app.processEvents();time.sleep(.001)
                if time.monotonic()-begin>2:raise AssertionError('Repeated pause timed out')
            pauses.append((time.monotonic()-begin)*1000)
        data={'idle':idle,'one_view_economical':one,'two_views_economical':two,'pause_latency_ms':max(pauses),'pause_samples_ms':pauses,'paused':paused}
        identity=w.lifecycle.identity;settings=w.project.settings;revisions=dict(w.revisions)
        w.run_simulation();w.mode_combo.setCurrentText('Performance');observe(.3);data['two_views_performance']=observe(3)
        data['mode_preserved_run_grid_measurements']=identity==w.lifecycle.identity and settings==w.project.settings and revisions==w.revisions
        data['passed']=all(v['displayed_frames_per_second']>=20 and v['steps_per_second']<=240 and v['displayed_frames_per_second']<=30 and v['rss_peak_bytes']<=1024**3 for v in (one,two)) and max(pauses)<100 and all(v['process_cpu_seconds_per_second']<=.1 and v['steps_per_second']==0 and v['displayed_frames_per_second']==0 for v in (idle,paused)) and data['mode_preserved_run_grid_measurements'] and 20<=data['two_views_performance']['displayed_frames_per_second']<=30 and data['two_views_performance']['rss_peak_bytes']<=1024**3
        w.pause_simulation();observe(.1)
        if backend=='mps':data['mps_allocated_bytes']=torch.mps.current_allocated_memory()
        report[backend]=data
finally:
    w.lifecycle.dirty=False;w.close();app.processEvents()
report['passed']=all(report[k]['passed'] for k in ('cpu','mps') if k in report)
output=Path('local-results/resource-results.json');output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2));raise SystemExit(0 if report['passed'] else 1)
