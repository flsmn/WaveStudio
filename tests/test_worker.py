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
        lifecycle.run()
        worker.submit('start',lifecycle.identity,compile_project(p),'cpu')
        restarted = frame_from(worker)
        assert restarted.identity != first.identity
        assert restarted.steps <= 8
    finally:
        worker.shutdown()
        assert worker.wait(5000)
