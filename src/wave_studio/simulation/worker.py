"""A single QThread owns the solver; bounded commands and latest-only frames."""
from collections import deque
from dataclasses import dataclass
from threading import Condition, Lock
from time import monotonic
from PySide6.QtCore import QThread
import numpy as np
from wave_sim2d.wave_simulation import WaveSimulator2D
from .lifecycle import Identity


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

    def __init__(self,parent=None):
        super().__init__(parent)
        self.latest = Latest()
        self._condition = Condition()
        self._commands = deque()
        self._closing = False

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
        sim, identity, running = None, None, False
        last_frame = 0.0
        views={'Field'}
        mode='Economical'
        def publish():
            if sim is None: return
            intensity=None
            if 'Intensity' in views:
                intensity=sim.measurements.intensity.detach().cpu().numpy().copy()
                intensity.setflags(write=False)
            self.latest.put(Frame(identity,sim.t,sim.steps,sim.snapshot() if 'Field' in views else None,intensity,sim.measurements.results(),str(sim.device),not running))
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
                        sim = None  # release old backend state before allocating a new one
                        prepared,specs=(scene if isinstance(scene,tuple) else (scene,()))
                        sim = WaveSimulator2D.from_scene(prepared,device=device)
                        sim.measurements.configure(specs,0)
                        running = True
                        last_frame = 0
                    elif action == 'resume':
                        if sim is None:
                            raise RuntimeError('No paused simulation is available. Reset and press Run.')
                        running = True
                    elif action == 'pause':
                        running = False
                        if sim is not None:
                            publish()
                    elif action == 'reset':
                        running, sim = False, None
                        self.latest.take()
                    elif action == 'step':
                        if sim is None or running:
                            raise RuntimeError('Step requires a paused, initialized simulation.')
                        sim.step()
                        publish()
                    elif action == 'detectors':
                        if sim is not None:
                            sim.measurements.configure(scene,sim.t)
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
                    block=max(1,min(self.BLOCK_STEPS,1048576//(sim.grid.nx*sim.grid.ny)))
                    sim.step(block)
                    now = monotonic()
                    if now-last_frame >= self.DISPLAY_INTERVAL:
                        publish()
                        last_frame = now
                    # Separate compute and display limits. Commands wake the wait immediately.
                    with self._condition:
                        if not self._commands and not self._closing:
                            self._condition.wait(max(0,self.BLOCK_INTERVAL-(monotonic()-started)) if mode=="Economical" else 0)
            except Exception as error:
                running, sim = False, None
                self.latest.put(Failure(identity,str(error) or type(error).__name__))
        sim = None
