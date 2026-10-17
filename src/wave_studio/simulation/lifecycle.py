"""Deterministic lifecycle, without Qt, torch, or a numerical solver."""
from dataclasses import dataclass
from enum import Enum
from uuid import uuid4


class State(str,Enum):
    READY = 'Ready'
    RUNNING = 'Running'
    PAUSED = 'Paused'
    CHANGED = 'Setup changed — press Run to start a new experiment'
    ERROR = 'Error'


@dataclass(frozen=True)
class Identity:
    project_id: str
    scene_revision: int
    run_id: str
    generation: int


class Lifecycle:
    def __init__(self,project_id):
        self.project_id = project_id
        self.scene_revision = 0
        self.generation = 0
        self.run_id = ''
        self.state = State.READY
        self.error = ''
        self.dirty = False

    @property
    def identity(self):
        return Identity(self.project_id,self.scene_revision,self.run_id,self.generation)

    @property
    def can_step(self):
        return self.state == State.PAUSED and bool(self.run_id)

    def run(self):
        fresh = self.state != State.PAUSED or not self.run_id
        if fresh:
            self.run_id = str(uuid4())
            self.generation += 1
        self.error = ''
        self.state = State.RUNNING
        return fresh

    def pause(self):
        if self.state == State.RUNNING:
            self.state = State.PAUSED

    def physical_change(self):
        if self.state == State.RUNNING:
            raise ValueError('Pause the simulation before editing the physical setup.')
        self.scene_revision += 1
        self.generation += 1
        self.run_id = ''
        self.state = State.CHANGED
        self.dirty = True

    def reset(self):
        self.generation += 1
        self.run_id = ''
        self.state = State.READY
        self.error = ''

    def fail(self,message):
        self.generation += 1
        self.run_id = ''
        self.state = State.ERROR
        self.error = message

    def accepts(self,identity):
        return bool(self.run_id) and identity == self.identity and self.state in (State.RUNNING,State.PAUSED)
