"""A single QThread owns the solver; bounded commands and latest-only frames."""
from collections import deque
from dataclasses import dataclass
from threading import Condition, Lock
from time import monotonic
from PySide6.QtCore import QThread
import numpy as np
import torch
import torch.nn.functional as functional
from wave_sim2d.wave_simulation import WaveSimulator2D
from .lifecycle import Identity
from .activity import RunActivity


@dataclass(frozen=True)
class Frame:
    identity: Identity
    time: float
    steps: int
    field: np.ndarray | None
    intensity: np.ndarray | None = None
    profiles: dict | None = None
    backend: str = "cpu"
    paused: bool = False
    preview: bool = False


def display_snapshot(tensor,max_axis=None):
    """Bound live transfer/render cost. Paused frames retain every grid cell."""
    value=tensor.detach()
    if max_axis and max(value.shape)>max_axis:
        ratio=max_axis/max(value.shape)
        size=tuple(max(1,round(n*ratio)) for n in value.shape)
        value=functional.interpolate(value[None,None],size=size,mode='bilinear',align_corners=False)[0,0]
    result=value.cpu().numpy().copy();result.setflags(write=False)
    return result


@dataclass(frozen=True)
class Failure:
    identity: Identity
    message: str


class Latest:
    def __init__(self):
        self._lock = Lock()
        self._value = None

    def put(self,value):
        with self._lock:
            self._value = value

    def take(self):
        with self._lock:
            value, self._value = self._value, None
            return value


class SimulationWorker(QThread):
    BLOCK_STEPS = 4
    DISPLAY_INTERVAL = 1/30
    BLOCK_INTERVAL = 1/60
    DISPLAY_AXIS_LIMIT = 1024

    def __init__(self,parent=None):
        super().__init__(parent)
        self.latest = Latest()
        self._condition = Condition()
        self._commands = deque()
        self._closing = False
        self._reset_identity = None
        self.activity = RunActivity()

    def reset_completed(self,identity):
        with self._condition:return self._reset_identity==identity

    def submit(self,action,identity,scene=None,device='cpu'):
        with self._condition:
            if self._closing:
                return
            if len(self._commands) >= 32:
                raise RuntimeError('Too many pending simulation commands. Wait for the current action.')
            self._commands.append((action,identity,scene,device))
            self._condition.notify()

    def shutdown(self):
        with self._condition:
            self._closing = True
            self._commands.clear()
            self._condition.notify()

    def run(self):
        try:self._run()
        finally:self._end_work()

    def _begin_work(self):
        if self.activity.supported and hasattr(QThread,'QualityOfService'):
            self.setServiceLevel(QThread.QualityOfService.High)
        self.activity.begin()

    def _end_work(self):
        self.activity.end()
        if self.activity.supported and hasattr(QThread,'QualityOfService'):
            self.setServiceLevel(QThread.QualityOfService.Auto)

    def _run(self):
        sim, identity, running = None, None, False
        last_frame = 0.0
        views={'Field'}
        mode='Economical'
        def publish():
            if sim is None: return
            limit=self.DISPLAY_AXIS_LIMIT if running else None
            preview=bool(limit and max(sim.grid.shape)>limit)
            intensity=None
            if 'Intensity' in views:
                intensity=display_snapshot(sim.measurements.intensity,limit)
            self.latest.put(Frame(identity,sim.t,sim.steps,display_snapshot(sim.u,limit) if 'Field' in views else None,intensity,sim.measurements.results(),str(sim.device),not running,preview))
        while True:
            with self._condition:
                while not self._closing and not self._commands and not running:
                    self._condition.wait()
                if self._closing:
                    break
                command = self._commands.popleft() if self._commands else None
            try:
                if command:
                    action, identity, scene, device = command
                    if action == 'start':
                        self._begin_work()
                        sim = None  # release old backend state before allocating a new one
                        prepared,specs=(scene if isinstance(scene,tuple) else (scene,()))
                        sim = WaveSimulator2D.from_scene(prepared,device=device)
                        sim.measurements.configure(specs,0,field=sim.u)
                        running = True
                        last_frame = 0
                    elif action == 'resume':
                        if sim is None:
                            raise RuntimeError('No paused simulation is available. Reset and press Run.')
                        self._begin_work();running = True
                    elif action == 'pause':
                        running = False
                        if sim is not None:
                            publish()
                        self._end_work()
                    elif action == 'reset':
                        self._end_work()
                        was_mps=sim is not None and sim.device.type=='mps'
                        running, sim = False, None
                        self.latest.take()
                        if was_mps:torch.mps.empty_cache()
                        with self._condition:self._reset_identity=identity
                    elif action == 'step':
                        if sim is None or running:
                            raise RuntimeError('Step requires a paused, initialized simulation.')
                        self._begin_work()
                        try:sim.step();publish()
                        finally:self._end_work()
                    elif action == 'detectors':
                        if sim is not None:
                            sim.measurements.configure(scene,sim.t,field=sim.u)
                            publish()
                    elif action == 'views':
                        views=set(scene)
                        publish()
                    elif action == 'mode':
                        mode=scene
                    else:
                        raise RuntimeError('Unknown simulation command.')
                    continue
                if running:
                    started = monotonic()
                    # Keep command boundaries short when quality selects millions of cells.
                    block=max(1,min(1 if sim.device.type=='mps' else self.BLOCK_STEPS,1048576//(sim.grid.nx*sim.grid.ny)))
                    sim.step(block)
                    now = monotonic()
                    if now-last_frame >= self.DISPLAY_INTERVAL:
                        publish()
                        last_frame = now
                    # Separate compute and display limits. Commands wake the wait immediately.
                    with self._condition:
                        if not self._commands and not self._closing:
                            self._condition.wait(max(0,self.BLOCK_INTERVAL*block/self.BLOCK_STEPS-(monotonic()-started)) if mode=="Economical" else 0)
            except Exception as error:
                self._end_work()
                running, sim = False, None
                self.latest.put(Failure(identity,str(error) or type(error).__name__))
        was_mps=sim is not None and sim.device.type=='mps'
        sim = None
        if was_mps:torch.mps.empty_cache()
