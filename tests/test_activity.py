import time
import pytest
from wave_studio.simulation.activity import RunActivity,DarwinActivity
from wave_studio.simulation.worker import SimulationWorker,Frame,Failure
from wave_studio.simulation.lifecycle import Lifecycle
from wave_studio.simulation.compiler import compile_project
from wave_studio.domain.project import Project


class Backend:
    def __init__(self):self.tokens=[];self.ended=[]
    def begin(self):
        token=object();self.tokens.append(token);return token
    def end(self,token):self.ended.append(token)


def test_activity_balanced_tokens_no_sleep_prevention_and_portable_noop():
    backend=Backend();activity=RunActivity(lambda:backend,platform='darwin')
    activity.begin();activity.begin();assert activity.active and len(backend.tokens)==1
    activity.end();activity.end();assert not activity.active and backend.ended==backend.tokens
    activity.begin();activity.end();assert activity.begins==activity.ends==2
    assert not DarwinActivity.OPTIONS & (1<<20) and not DarwinActivity.OPTIONS & (1<<40)
    other=RunActivity(lambda:pytest.fail('Native API called on another platform'),platform='linux')
    other.begin();other.end();assert not other.active


def test_activity_api_failure_does_not_interrupt_simulation():
    calls=[]
    def unavailable():calls.append(1);raise OSError('unavailable API')
    activity=RunActivity(unavailable,platform='darwin');activity.begin();activity.begin();activity.end()
    assert activity.failed and not activity.active and calls==[1]


def wait_for(worker,predicate):
    deadline=time.monotonic()+4
    while time.monotonic()<deadline:
        value=worker.latest.take()
        if value is not None and predicate(value):return value
        time.sleep(.005)
    pytest.fail('Worker response timed out')


def test_worker_activity_pause_step_reset_and_shutdown():
    import torch
    torch.set_num_threads(1)
    backend=Backend();w=SimulationWorker();w.activity=RunActivity(lambda:backend,platform='darwin')
    p=Project();life=Lifecycle(p.id);life.run();scene=compile_project(p);w.start()
    try:
        w.submit('start',life.identity,scene,'cpu');wait_for(w,lambda f:isinstance(f,Frame) and f.steps>0)
        assert w.activity.active
        w.submit('pause',life.identity);wait_for(w,lambda f:isinstance(f,Frame) and f.paused)
        assert not w.activity.active
        w.submit('step',life.identity);wait_for(w,lambda f:isinstance(f,Frame))
        assert not w.activity.active and w.activity.begins==2
        w.submit('resume',life.identity);wait_for(w,lambda f:isinstance(f,Frame) and not f.paused)
        w.submit('reset',life.identity)
        deadline=time.monotonic()+2
        while not w.reset_completed(life.identity) and time.monotonic()<deadline:time.sleep(.005)
        assert w.reset_completed(life.identity) and not w.activity.active
        w.submit('start',life.identity,scene,'cpu');wait_for(w,lambda f:isinstance(f,Frame))
    finally:w.shutdown();assert w.wait(4000)
    assert not w.activity.active and backend.ended==backend.tokens
    if hasattr(w,'serviceLevel'):assert w.serviceLevel().name=='Auto'


def test_worker_failure_releases_activity(monkeypatch):
    from wave_sim2d.wave_simulation import WaveSimulator2D
    def fail(*args):raise RuntimeError('controlled solver failure')
    monkeypatch.setattr(WaveSimulator2D,'step',fail)
    backend=Backend();w=SimulationWorker();w.activity=RunActivity(lambda:backend,platform='darwin');w.start()
    life=Lifecycle('failure');life.run()
    try:
        w.submit('start',life.identity,compile_project(Project()),'cpu')
        wait_for(w,lambda f:isinstance(f,Failure))
        assert not w.activity.active and backend.ended==backend.tokens
    finally:w.shutdown();assert w.wait(4000)
