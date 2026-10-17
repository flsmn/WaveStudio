"""Small deterministic checks for T05's thread ownership and stale data risk."""
import time
import pytest
from wave_studio.domain.project import Project
from wave_studio.simulation.compiler import compile_project
from wave_studio.simulation.lifecycle import Lifecycle
from wave_studio.simulation.worker import SimulationWorker, Frame, Failure


def frame_from(worker, predicate=lambda f: True):
    deadline = time.monotonic()+5
    while time.monotonic() < deadline:
        frame = worker.latest.take()
        if isinstance(frame,Failure): pytest.fail(frame.message)
        if isinstance(frame,Frame) and predicate(frame): return frame
        time.sleep(.005)
    pytest.fail('Timed out waiting for a worker frame')


def test_single_worker_pause_step_reset_and_shutdown():
    import torch
    torch.set_num_threads(1)
    p = Project()
    lifecycle = Lifecycle(p.id)
    worker = SimulationWorker()
    worker.start()
    try:
        lifecycle.run()
        worker.submit('start',lifecycle.identity,compile_project(p),'cpu')
        first = frame_from(worker)
        lifecycle.pause()
        worker.submit('pause',lifecycle.identity)
        paused = frame_from(worker,lambda f: f.steps >= first.steps)
        # Drain the pause acknowledgement before testing exact Step semantics.
        time.sleep(.05)
        ack = worker.latest.take()
        if ack is not None: paused = ack
        worker.submit('step',lifecycle.identity)
        stepped = frame_from(worker)
        assert stepped.steps == paused.steps+1
        assert stepped.identity == first.identity
        assert not stepped.field.flags.writeable
        lifecycle.reset()
        worker.submit('reset',lifecycle.identity)
        assert not lifecycle.accepts(stepped.identity)
        time.sleep(.05)
        assert worker.latest.take() is None
        assert worker.reset_completed(lifecycle.identity)
        lifecycle.run()
        worker.submit('start',lifecycle.identity,compile_project(p),'cpu')
        restarted = frame_from(worker)
        assert restarted.identity != first.identity
        assert restarted.steps <= 8
    finally:
        worker.shutdown()
        assert worker.wait(5000)


def test_worker_failure_stops_without_automatic_restart(monkeypatch):
    from wave_studio.simulation.worker import Failure
    from wave_sim2d.wave_simulation import WaveSimulator2D
    calls=[]
    def fail(self,*args):
        calls.append(1)
        raise RuntimeError('Controlled backend failure')
    monkeypatch.setattr(WaveSimulator2D,'step',fail)
    p=Project();c=Lifecycle(p.id);c.run();worker=SimulationWorker();worker.start()
    try:
        worker.submit('start',c.identity,compile_project(p),'cpu')
        deadline=time.monotonic()+3
        result=None
        while time.monotonic()<deadline:
            result=worker.latest.take()
            if isinstance(result,Failure):break
            time.sleep(.005)
        assert isinstance(result,Failure) and 'Controlled backend failure' in result.message
        time.sleep(.03)
        assert len(calls)==1 and worker.latest.take() is None
    finally:
        worker.shutdown();assert worker.wait(5000)


def test_live_preview_keeps_full_paused_frames_and_does_not_mutate_solver(monkeypatch):
    import torch,numpy as np
    from wave_studio.simulation.worker import display_snapshot
    field=torch.arange(128*64,dtype=torch.float32).reshape(64,128);original=field.clone()
    image=display_snapshot(field,32)
    assert image.shape==(16,32) and not image.flags.writeable
    assert torch.equal(field,original)
    np.testing.assert_array_equal(display_snapshot(field),field.numpy())
    monkeypatch.setattr(SimulationWorker,'DISPLAY_AXIS_LIMIT',32)
    p=Project();lifecycle=Lifecycle(p.id);lifecycle.run();worker=SimulationWorker();worker.start()
    try:
        worker.submit('start',lifecycle.identity,compile_project(p),'cpu')
        live=frame_from(worker,lambda f:f.steps>0)
        assert live.preview and live.field.shape==(32,32)
        worker.submit('pause',lifecycle.identity)
        paused=frame_from(worker,lambda f:f.paused)
        assert not paused.preview and paused.field.shape==(256,256)
        worker.submit('step',lifecycle.identity)
        stepped=frame_from(worker,lambda f:f.steps>paused.steps)
        assert stepped.paused and not stepped.preview and stepped.field.shape==(256,256)
    finally:worker.shutdown();assert worker.wait(5000)
