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
    quality: str = 'Custom'
    buffer_limit_mib: int = 512
    max_axis_cells: int = 4096


@dataclass(frozen=True)
class DisplaySettings:
    view: str = 'Field'
    contrast: float = .25
    intensity_range: float = .0002
    theme: str = 'Dark'
    secondary_view: str = 'Intensity'
    secondary_visible: bool = False
    text_scale: float = 1.0


@dataclass(frozen=True)
class Project:
    id: str = field(default_factory=identifier)
    name: str = 'Point source experiment'
    reference_length: float = 1.0
    settings: SimulationSettings = field(default_factory=SimulationSettings)
    objects: tuple[SourceObject | MaterialObject | WallObject, ...] = field(default_factory=lambda: (SourceObject(),))
    display: DisplaySettings = field(default_factory=DisplaySettings)
    detectors: tuple = ()
    references: tuple = ()
    compute_mode: str = 'Economical'

    def validate(self):
        def number(v, name, positive=False):
            if isinstance(v,bool) or not isinstance(v,(int,float)) or not math.isfinite(v) or positive and v <= 0:
                raise ValueError(f'{name} must be a finite' + (' positive number.' if positive else ' number.'))
        if not isinstance(self.id,str) or not self.id or not isinstance(self.name,str) or not self.name.strip() or len(self.name)>200:
            raise ValueError('Project ID and name must be nonempty strings; names are limited to 200 characters.')
        for obj in self.objects+self.detectors:
            if not isinstance(obj.id,str) or not obj.id or not isinstance(obj.name,str) or not obj.name.strip() or len(obj.name)>200:
                raise ValueError('Object IDs and names must be nonempty strings; names are limited to 200 characters.')
        if type(self.display.secondary_visible) is not bool: raise ValueError('Second view visibility must be a boolean.')
        number(self.reference_length, 'Reference length', True)
        s = self.settings
        for name in ('width','height','dx','courant'):
            number(getattr(s,name),name,True)
        for name in ('border_width','border_rate'):
            number(getattr(s,name),name)
            if getattr(s,name) < 0: raise ValueError(f'{name} must be nonnegative.')
        if s.quality not in ('Custom','Preview','Balanced','High Quality'):raise ValueError('Unknown quality setting.')
        if s.device not in ('cpu','mps','auto'):
            raise ValueError('This prototype offers CPU and MPS only.')
        if any(abs(v/s.dx-round(v/s.dx)) > 1e-7 for v in (s.width,s.height)):
            raise ValueError('Domain dimensions must be integer multiples of grid spacing.')
        from .resources import rejection
        reason=rejection(s,round(s.width/s.dx),round(s.height/s.dx))
        if reason:raise ValueError(reason)
        if not self.id or len({o.id for o in self.objects}) != len(self.objects) or any(not o.id for o in self.objects):
            raise ValueError('Every object must have a distinct nonempty ID.')
        for obj in self.objects:
            if isinstance(obj,SourceObject):
                number(obj.wavelength,'Wavelength',True)
                number(obj.amplitude,'Amplitude')
                number(obj.phase,'Phase')
                if obj.amplitude < 0: raise ValueError('Amplitude must be nonnegative.')
            elif not isinstance(obj,(MaterialObject,WallObject,LensObject)):
                raise ValueError('Unsupported scene object.')
        if len(self.objects)>256 or len(self.detectors)>16 or len(self.references)>4:
            raise ValueError('Limit: 256 scene objects, 16 detectors and 4 reference profiles.')
        ids=[o.id for o in self.objects]+[d.id for d in self.detectors]
        if len(ids)!=len(set(ids)): raise ValueError('Object and detector IDs must be unique.')
        if self.display.view not in ('Field','Intensity','Material') or self.display.secondary_view not in ('Field','Intensity','Material') or self.display.theme not in ('Dark','Light'):
            raise ValueError('Unsupported display settings.')
        if self.display.text_scale not in (1.,1.25,1.5):raise ValueError('Text size must be 100%, 125% or 150%.')
        number(self.display.contrast,'Display range',True)
        number(self.display.intensity_range,'Intensity display range',True)
        if self.compute_mode not in ('Economical','Performance'): raise ValueError('Unknown compute mode.')
        return self


def with_source(project, **changes):
    source = next(o for o in project.objects if isinstance(o,SourceObject))
    updated = replace(source, **changes)
    return replace(project,objects=tuple(updated if o.id == source.id else o for o in project.objects))


@dataclass(frozen=True)
class LensObject:
    id: str = field(default_factory=identifier)
    name: str = 'Biconvex lens'
    x: float = 18
    y: float = 16
    radius: float = 12
    aperture: float = 10
    angle: float = 0
    refractive_index: float = 1.5
    damping_rate: float = 0


@dataclass(frozen=True)
class DetectorObject:
    id: str = field(default_factory=identifier)
    name: str = 'Detector line'
    start: tuple[float,float] = (26,6)
    end: tuple[float,float] | None = (26,26)
    samples: int = 161
    settling: float = 32
    window: float = 16
