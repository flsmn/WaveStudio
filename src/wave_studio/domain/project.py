from dataclasses import dataclass, field, replace
import math
from uuid import uuid4


def identifier():
    return str(uuid4())


@dataclass(frozen=True)
class SourceObject:
    id: str = field(default_factory=identifier)
    name: str = 'Point source'
    start: tuple[float, float] = (16.0, 16.0)
    end: tuple[float, float] | None = None
    wavelength: float = 2.0
    amplitude: float = 1.0
    phase: float = 0.0


@dataclass(frozen=True)
class MaterialObject:
    id: str = field(default_factory=identifier)
    name: str = 'Material'
    vertices: tuple[tuple[float,float], ...] = ((18.,8.),(24.,8.),(24.,24.),(18.,24.))
    refractive_index: float = 1.5
    damping_rate: float = 0.0


@dataclass(frozen=True)
class WallObject:
    id: str = field(default_factory=identifier)
    name: str = 'Wall'
    x: float = 20
    y: float = 0
    width: float = 1
    height: float = 32


@dataclass(frozen=True)
class SimulationSettings:
    width: float = 32
    height: float = 32
    dx: float = .125
    courant: float = .5
    border_width: float = 3
    border_rate: float = 2
    device: str = 'cpu'


@dataclass(frozen=True)
class DisplaySettings:
    view: str = 'Field'
    contrast: float = 1.0
    theme: str = 'Dark'


@dataclass(frozen=True)
class Project:
    id: str = field(default_factory=identifier)
    name: str = 'Point source experiment'
    reference_length: float = 1.0
    settings: SimulationSettings = field(default_factory=SimulationSettings)
    objects: tuple[SourceObject | MaterialObject | WallObject, ...] = field(default_factory=lambda: (SourceObject(),))
    display: DisplaySettings = field(default_factory=DisplaySettings)

    def validate(self):
        def number(v, name, positive=False):
            if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or positive and v <= 0:
                raise ValueError(f'{name} must be a finite' + (' positive number.' if positive else ' number.'))
        number(self.reference_length, 'Reference length', True)
        s = self.settings
        for name in ('width','height','dx','courant'):
            number(getattr(s,name),name,True)
        for name in ('border_width','border_rate'):
            number(getattr(s,name),name)
            if getattr(s,name) < 0: raise ValueError(f'{name} must be nonnegative.')
        if s.device not in ('cpu','mps','auto'):
            raise ValueError('This prototype offers CPU and MPS only.')
        if any(abs(v/s.dx-round(v/s.dx)) > 1e-7 for v in (s.width,s.height)):
            raise ValueError('Domain dimensions must be integer multiples of grid spacing.')
        if not self.id or len({o.id for o in self.objects}) != len(self.objects) or any(not o.id for o in self.objects):
            raise ValueError('Every object must have a distinct nonempty ID.')
        for obj in self.objects:
            if isinstance(obj,SourceObject):
                number(obj.wavelength,'Wavelength',True)
                number(obj.amplitude,'Amplitude')
                number(obj.phase,'Phase')
                if obj.amplitude < 0: raise ValueError('Amplitude must be nonnegative.')
            elif not isinstance(obj,(MaterialObject,WallObject)):
                raise ValueError('Unsupported scene object.')
        return self


def with_source(project, **changes):
    source = next(o for o in project.objects if isinstance(o,SourceObject))
    updated = replace(source, **changes)
    return replace(project,objects=tuple(updated if o.id == source.id else o for o in project.objects))
