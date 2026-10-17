"""Real editor/MPS resource follow-up; criteria in docs/BALANCED_MAC_PLAN.md."""
from dataclasses import replace
import json,os,platform,resource,subprocess,time
from pathlib import Path
import torch
from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from wave_studio import __version__
from wave_sim2d import __version__ as engine_version
from wave_studio.examples import example
from wave_studio.domain.quality import estimate
from wave_studio.persistence.projects import encode,decode
from wave_studio.ui.editor import MainWindow


def main():
    torch.set_num_threads(1)
    if not torch.backends.mps.is_available():raise RuntimeError('Actual MPS device required for this acceptance.')
    os.environ['WAVESTUDIO_RECOVERY_DIR']='/tmp/wave-balanced-recovery'
    app=QApplication([]);app.setStyle('Fusion');w=MainWindow();w.resize(1320,870);w.show()
    report={'platform':platform.platform(),'machine':'Apple M1 / 8 GiB','studio':__version__,'engine':engine_version,'device':'mps','criteria':'docs/BALANCED_MAC_PLAN.md','measurements':{},'pause_samples_ms':[], 'note':'Process RSS and MPS allocations overlap on unified memory; do not add them. Resource/interaction acceptance only; no new focus certification.'}
    output=Path('docs/balanced-resource-results.json');last_beat=time.monotonic();gaps=[]
    def heartbeat():
        nonlocal last_beat
        now=time.monotonic();gaps.append((now-last_beat)*1000);last_beat=now
    timer=QTimer();timer.setInterval(10);timer.timeout.connect(heartbeat);timer.start()
    def reset_heartbeat():
        nonlocal last_beat
        gaps.clear();last_beat=time.monotonic()
    def sample():
        return {'rss_peak_bytes':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,'mps_current_bytes':torch.mps.current_allocated_memory(),'mps_driver_bytes':torch.mps.driver_allocated_memory()}
    def observe(seconds):
        reset_heartbeat();start=time.monotonic();cpu=time.process_time();frames=0;last=w.frame.steps if w.frame else 0;first=last
        while time.monotonic()-start<seconds:
            app.processEvents()
            if w.frame and w.frame.steps!=last:frames+=1;last=w.frame.steps
            time.sleep(.001)
        elapsed=time.monotonic()-start
        return {**sample(),'wall_seconds':elapsed,'displayed_frames_per_second':frames/elapsed,'steps_per_second':(last-first)/elapsed,'process_cpu_seconds_per_second':(time.process_time()-cpu)/elapsed,'gui_heartbeat_max_gap_ms':max(gaps,default=0)}
    def wait_for(condition,seconds):
        deadline=time.monotonic()+seconds
        while not condition():
            app.processEvents();time.sleep(.001)
            if time.monotonic()>deadline:raise AssertionError('Timed out: '+w.message.text())
    def run():
        start=time.monotonic();w.run_simulation();return (time.monotonic()-start)*1000
    def pause():
        start=time.monotonic();w.pause_simulation();wait_for(lambda:w.frame is not None and w.frame.paused,2)
        report['pause_samples_ms'].append((time.monotonic()-start)*1000)
    def swap():return subprocess.check_output(['/usr/sbin/sysctl','vm.swapusage'],text=True).strip()
    try:
        report['system_swap_before']=swap();report['baseline']=sample()
        p=example('Biconvex lens');p=replace(p,settings=replace(p.settings,buffer_limit_mib=768,device='mps'))
        e=estimate(p,'Balanced');assert e.supported
        p=replace(p,settings=replace(p.settings,quality='Balanced',dx=e.dx))
        report.update(grid=[e.nx,e.ny],dx=e.dx,estimated_buffer_bytes=e.estimated_bytes,buffer_limit_mib=768,max_axis_cells=4096)
        start=time.monotonic();w.replace_project(p);report['preparation_seconds']=time.monotonic()-start
        report['resource_json_roundtrip']=decode(encode(p))==p
        Path('/tmp/wave-balanced.wave.json').write_bytes(encode(p))
        report['run_handler_ms']=run();start=time.monotonic();wait_for(lambda:w.frame is not None and w.frame.steps>=4,10);report['first_frame_seconds']=time.monotonic()-start
        report['live_display_shape']=list(w.frame.field.shape);report['live_preview_marked']=w.frame.preview
        observe(1);report['measurements']['one_view_economical']=observe(10)
        pause();steps=w.frame.steps;report['paused_display_shape']=list(w.frame.field.shape);report['paused_full_detail']=w.frame.field.shape==w.scene.grid.shape and not w.frame.preview;report['measurements']['paused']=observe(1);report['paused_steps_stable']=w.frame.steps==steps
        w.step_simulation();wait_for(lambda:w.frame.steps>steps,2);report['exact_step']=w.frame.steps==steps+1 and w.frame.paused
        identity=w.lifecycle.identity
        report['resume_handler_ms']=run();wait_for(lambda:w.frame.steps>steps+1 and not w.frame.paused,2)
        w.secondary_action.setChecked(True);w.secondary_view.setCurrentText('Intensity');observe(1)
        report['measurements']['two_views_economical']=observe(10);pause()
        for _ in range(3):
            previous=w.frame.steps;run();wait_for(lambda:w.frame.steps>previous and not w.frame.paused,2);observe(.5);pause()
        previous=w.frame.steps;run();wait_for(lambda:w.frame.steps>previous and not w.frame.paused,2)
        w.mode_combo.setCurrentText('Performance');observe(1);report['measurements']['two_views_performance']=observe(10);pause()
        report['run_grid_measurements_preserved']=w.lifecycle.identity==identity and w.project.settings==p.settings and w.scene.grid.nx==e.nx
        report['paused_scene_screenshot']='docs/mac-artifacts/balanced-two-views.png';w.grab().save(report['paused_scene_screenshot'])
        start=time.monotonic();w.reset_simulation();report['reset_handler_ms']=(time.monotonic()-start)*1000
        # Driver allocations also include persistent backend/kernel state. The
        # worker acknowledges release after dropping the solver and empty_cache.
        wait_for(lambda:w.worker.reset_completed(w.lifecycle.identity),2)
        report['reset_release_ms']=(time.monotonic()-start)*1000;report['after_reset']=sample()
        report['reset_stopped']=w.frame is None and not w.lifecycle.run_id
        # Shutdown while actively computing also has to remain bounded.
        run();wait_for(lambda:w.frame is not None and w.frame.steps>=4,10)
        start=time.monotonic();w.lifecycle.dirty=False;w.close();report['active_shutdown_ms']=(time.monotonic()-start)*1000
        report['worker_stopped']=not w.worker.isRunning();report['system_swap_after']=swap()
        metrics=report['measurements'];active=[v for k,v in metrics.items() if k!='paused']
        report['passed']=(max(report['pause_samples_ms'])<250 and all(v['gui_heartbeat_max_gap_ms']<250 for v in active) and max(report[k] for k in ('run_handler_ms','resume_handler_ms','reset_handler_ms'))<250 and report['preparation_seconds']<5 and report['first_frame_seconds']<10 and report['reset_release_ms']<2000 and report['active_shutdown_ms']<2000 and all(v['rss_peak_bytes']<2*1024**3 and v['mps_driver_bytes']<2*1024**3 for v in metrics.values()) and all(report[k] for k in ('paused_steps_stable','exact_step','resource_json_roundtrip','run_grid_measurements_preserved','reset_stopped','worker_stopped','live_preview_marked','paused_full_detail')))
    except Exception as error:
        report['passed']=False;report['error']=str(error)
    finally:
        report['terminal_memory']=sample()
        timer.stop();w.lifecycle.dirty=False;w.close();app.processEvents()
        output.write_text(json.dumps(report,indent=2)+'\n');print(json.dumps(report,indent=2),flush=True)
    return 0 if report['passed'] else 1


if __name__=='__main__':raise SystemExit(main())
