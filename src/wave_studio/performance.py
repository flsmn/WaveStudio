"""Opt-in, reproducible editor/worker timing with the real Qt event loop."""
from dataclasses import replace
from functools import wraps
import ctypes,json,os,platform,resource,subprocess,sys,time
from pathlib import Path
import numpy as np
import torch
import pyqtgraph as pg
from PySide6 import __version__ as qt_binding_version
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QAccessible
import wave_sim2d
from wave_sim2d.wave_simulation import WaveSimulator2D
from wave_studio import __version__
from wave_studio.domain.quality import estimate
from wave_studio.examples import example
from wave_studio.simulation import worker
from wave_studio.ui.editor import MainWindow
from wave_studio.simulation.activity import DarwinActivity


def run_performance(output_directory,event_loop='native',seconds=10,without_activity=False,accessibility=False,warmup=2,case='all'):
    if not torch.backends.mps.is_available():raise RuntimeError('This check requires actual MPS hardware.')
    torch.set_num_threads(1)
    output=Path(output_directory);output.mkdir(parents=True,exist_ok=True)
    os.environ['WAVESTUDIO_RECOVERY_DIR']=str(output/'.recovery')
    app=QApplication([]);app.setApplicationName('Wave Studio');app.setOrganizationName('Wave Studio');app.setStyle('Fusion')
    timings={};enabled=False;received=0;states={};gaps=[];last_beat=time.monotonic();advance=None;finished=False
    thread_info={}
    def thread_qos():
        if sys.platform!='darwin':return None
        system=ctypes.CDLL('/usr/lib/libSystem.B.dylib')
        system.pthread_self.restype=ctypes.c_void_p
        system.pthread_get_qos_class_np.argtypes=[ctypes.c_void_p,ctypes.POINTER(ctypes.c_uint),ctypes.POINTER(ctypes.c_int)]
        system.pthread_get_qos_class_np.restype=ctypes.c_int
        qos=ctypes.c_uint();relative=ctypes.c_int()
        status=system.pthread_get_qos_class_np(system.pthread_self(),ctypes.byref(qos),ctypes.byref(relative))
        return {'status':status,'class':qos.value,'relative_priority':relative.value}
    native=DarwinActivity() if sys.platform=='darwin' else None
    def measure(name,func):
        @wraps(func)
        def call(*args,**kwargs):
            if not enabled:return func(*args,**kwargs)
            if name=='worker_step_ms' and 'worker_qos' not in thread_info:thread_info['worker_qos']=thread_qos()
            began=time.monotonic()
            try:return func(*args,**kwargs)
            finally:timings.setdefault(name,[]).append((time.monotonic()-began)*1000)
        return call
    original_step=WaveSimulator2D.step;original_snapshot=worker.display_snapshot;original_render=pg.ImageItem.render
    WaveSimulator2D.step=measure('worker_step_ms',original_step)
    worker.display_snapshot=measure('worker_display_transfer_ms',original_snapshot)
    pg.ImageItem.render=measure('image_render_ms',original_render)
    class Window(MainWindow):
        def _poll(self):
            nonlocal received,last_beat
            now=time.monotonic()
            if enabled:gaps.append((now-last_beat)*1000)
            last_beat=now
            before=self.frame
            super()._poll()
            if enabled and self.frame is not None and self.frame is not before:received+=1
            if advance is not None:advance()
        _draw=measure('gui_draw_ms',MainWindow._draw)
        _plot_profiles=measure('gui_profiles_ms',MainWindow._plot_profiles)
    w=Window();w.resize(1320,860);w.show()
    if accessibility:QAccessible.setActive(True);QAccessible.queryAccessibleInterface(w)
    if without_activity:w.worker.activity.supported=False
    p=example('Biconvex lens');p=replace(p,settings=replace(p.settings,buffer_limit_mib=768,device='mps'))
    e=estimate(p,'Balanced');p=replace(p,settings=replace(p.settings,quality='Balanced',dx=e.dx));w.replace_project(p)
    report={'version':__version__,'engine_version':wave_sim2d.__version__,'pid':os.getpid(),'frozen':bool(getattr(sys,'frozen',False)),'event_loop':event_loop,'platform':platform.platform(),'python':platform.python_version(),'torch':torch.__version__,'qt_binding':qt_binding_version,'pyqtgraph':pg.__version__,'engine_location':wave_sim2d.__file__,'application_location':__file__,'grid':[e.nx,e.ny],'seconds_per_case':seconds,'without_activity':without_activity,'measurements':{},'count_note':'Received latest frames and ImageItem conversions are distinct from compositor scanout FPS. Gaps refer to the production 33-ms poll; no helper Python timers.'}
    cases=[('one_view_economical',False,'Economical'),('two_views_economical',True,'Economical'),('two_views_performance',True,'Performance')]
    if case!='all':
        cases=[c for c in cases if c[0]==case]
        _,two,mode=cases[0];w.secondary_action.setChecked(two);w.mode_combo.setCurrentText(mode)
    report['case']=case;report['warmup_seconds']=warmup
    index=0;phase='starting';deadline=time.monotonic()+15;began=0;start_steps=0;cpu_start=0
    def stats(values):
        return {'count':len(values),'total':sum(values),'median':float(np.median(values)),'p95':float(np.percentile(values,95)),'max':max(values)} if values else {'count':0}
    def finish(error=None):
        nonlocal enabled,finished
        enabled=False;finished=True
        report['passed']=error is None
        if error:report['error']=error
        report['rss_peak_bytes']=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
        report['window']={'width':w.width(),'height':w.height(),'dpr':w.devicePixelRatioF(),'qt_platform':app.platformName()}
        report['thread_info']=thread_info
        w.lifecycle.dirty=False;w.close()
        report['activity_after_shutdown']={'active':w.worker.activity.active,'begins':w.worker.activity.begins,'ends':w.worker.activity.ends,'failed':w.worker.activity.failed}
        report['service_level_after_shutdown']=w.worker.serviceLevel().name if hasattr(w.worker,'serviceLevel') else 'unavailable'
        report['worker_stopped']=not w.worker.isRunning()
        (output/'performance-results.json').write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2),flush=True)
        app.quit()
    def tick():
        nonlocal index,phase,deadline,began,start_steps,cpu_start,enabled,received,timings,states,gaps,last_beat
        now=time.monotonic()
        if finished:return
        if phase=='starting':
            if w.frame is None or w.frame.steps<4:
                if now>deadline:finish('First frame timed out: '+w.message.text())
                return
            report['startup_seconds']=now-run_started
            phase='warmup';deadline=now+warmup
        if phase=='warmup' and now>=deadline:
            timings={};received=0;states={};gaps=[];last_beat=now;began=now;cpu_start=time.process_time();start_steps=w.frame.steps;enabled=True;phase='measuring';deadline=now+seconds
        if phase=='measuring':
            if w.frame is None:finish('Simulation failed: '+w.message.text());return
            state=app.applicationState().name+f'; accessibility={QAccessible.isActive()}; run_activity={w.worker.activity.active}';states[state]=states.get(state,0)+1
            if now<deadline:return
            enabled=False;elapsed=now-began
            report['measurements'][cases[index][0]]={'wall_seconds':elapsed,'received_frames_per_second':received/elapsed,'steps_per_second':(w.frame.steps-start_steps)/elapsed,'process_cpu_seconds_per_second':(time.process_time()-cpu_start)/elapsed,'timings':{k:stats(v) for k,v in timings.items()},'heartbeat_gap_ms':stats(gaps),'application_state_samples':states,'hud':w.rate_label.text(),'frame_shape':list(w.frame.field.shape),'backend':w.frame.backend}
            report['measurements'][cases[index][0]]['power_state']=native.power_state() if native else {}
            print(cases[index][0]+': '+str(report['measurements'][cases[index][0]]['received_frames_per_second']),flush=True)
            index+=1
            if index==len(cases):finish();return
            _,two,mode=cases[index];w.secondary_action.setChecked(two);w.mode_combo.setCurrentText(mode);phase='warmup';deadline=time.monotonic()+warmup
    advance=tick;run_started=time.monotonic();w.run_simulation()
    report['extra_python_timers']=False
    (output/'ready.json').write_text(json.dumps({'pid':os.getpid(),'version':__version__})+'\n')
    print('PERFORMANCE_READY',flush=True)
    try:
        if event_loop=='native':app.exec()
        else:
            while not finished:app.processEvents();time.sleep(.001)
    finally:
        WaveSimulator2D.step=original_step;worker.display_snapshot=original_snapshot;pg.ImageItem.render=original_render
        if w.worker.isRunning():w.lifecycle.dirty=False;w.close()
    return 0 if report.get('passed') else 1
