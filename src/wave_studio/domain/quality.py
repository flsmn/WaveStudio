"""Deterministic resolution selection, without Qt or device state."""
from dataclasses import dataclass
from fractions import Fraction
from functools import reduce
import math
from wave_sim2d.dispersion import phase_drift
from .project import SourceObject,MaterialObject,WallObject,LensObject
from .resources import buffer_bytes,rejection

PRESETS={'Preview':(10,2,math.pi),'Balanced':(12,4,math.pi/2),'High Quality':(20,6,math.pi/4)}


def wall_cell_ties(project,dx):
    """Half-open wall faces on cell centres can break reflection symmetry."""
    return any(abs((v/dx)%1-.5)<1e-8 for o in project.objects if isinstance(o,WallObject) for v in (o.x,o.y,o.x+o.width,o.y+o.height))


@dataclass(frozen=True)
class QualityEstimate:
    name: str
    dx: float
    nx: int
    ny: int
    estimated_bytes: int
    cells_per_wavelength: float
    cells_per_feature: float | None
    path: float
    phase_radians: float
    supported: bool
    reason: str


def measures(project):
    sources=[o for o in project.objects if isinstance(o,SourceObject)]
    materials=[o for o in project.objects if isinstance(o,(MaterialObject,LensObject))]
    wavelength=min((o.wavelength for o in sources),default=2.)
    index=max((o.refractive_index for o in materials),default=1.)
    features=[]
    for obj in project.objects:
        if isinstance(obj,WallObject):features.extend((obj.width,obj.height))
        elif isinstance(obj,LensObject):
            if not 0<obj.aperture<2*obj.radius:raise ValueError('Lens aperture must be between zero and twice its radius.')
            features.append(2*(obj.radius-math.sqrt(obj.radius**2-(obj.aperture/2)**2)))
        elif isinstance(obj,MaterialObject):
            # Minimum support width: exact for convex material polygons, including rotated rectangles.
            for a,b in zip(obj.vertices,obj.vertices[1:]+obj.vertices[:1]):
                length=math.dist(a,b)
                if length:
                    nx,ny=-(b[1]-a[1])/length,(b[0]-a[0])/length
                    projection=[x*nx+y*ny for x,y in obj.vertices]
                    width=max(projection)-min(projection)
                    if width>1e-12:features.append(width)
    starts=[p for source in sources for p in (source.start,source.end) if p is not None]
    targets=[p for detector in project.detectors for p in (detector.start,detector.end) if p is not None]
    path=max((math.dist(a,b) for a in starts for b in targets),default=math.hypot(max(0,project.settings.width-2*project.settings.border_width),max(0,project.settings.height-2*project.settings.border_width)))
    return wavelength,index,min(features,default=None),path


def estimate(project,name,dx=None):
    if name not in PRESETS and dx is None:raise ValueError('Unknown quality preset.')
    wavelength,index,feature,path=measures(project)
    s=project.settings
    if dx is None:
        cells,feature_cells,budget=PRESETS[name]
        target=min(wavelength/index/cells,feature/feature_cells if feature else math.inf)
        # A rational common domain unit avoids power-of-two over-refinement while
        # retaining square cells and the exact physical domain on both axes.
        sizes=[Fraction(str(v)).limit_denominator(1000000) for v in (s.width,s.height)]
        denominator=math.lcm(*(v.denominator for v in sizes))
        unit=math.gcd(*(v.numerator*(denominator//v.denominator) for v in sizes))/denominator
        for _ in range(160):
            divisions=max(1,math.ceil(unit/target))
            dx=unit/divisions
            nx,ny=round(s.width/dx),round(s.height/dx)
            if wall_cell_ties(project,dx):
                target=unit/(divisions+1)
                continue
            if phase_drift(wavelength,index,dx,s.courant,path)<=budget:break
            target=dx*.9
        else:raise ValueError('Could not select a bounded quality grid.')
    nx,ny=round(s.width/dx),round(s.height/dx)
    memory=buffer_bytes(nx,ny)
    reason=rejection(s,nx,ny)
    supported=not reason
    return QualityEstimate(name,dx,nx,ny,memory,wavelength/(index*dx),feature/dx if feature else None,path,phase_drift(wavelength,index,dx,s.courant,path),supported,reason)
