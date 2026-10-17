from dataclasses import replace
from .domain.project import Project,SimulationSettings,SourceObject,MaterialObject,WallObject,LensObject,DetectorObject


def _make_example(name):
    if name=='Double slit':
        return Project(name=name,settings=SimulationSettings(72,64,.25,.5,8,2,'cpu'),objects=(SourceObject(start=(14,32),wavelength=2),WallObject(name='Lower wall',x=30,y=0,width=.5,height=28.5),WallObject(name='Centre wall',x=30,y=29.5,width=.5,height=5),WallObject(name='Upper wall',x=30,y=35.5,width=.5,height=28.5)),detectors=(DetectorObject(start=(52,24),end=(52,40),samples=257,settling=60,window=24),))
    if name=='Refraction':
        import math
        a=math.radians(25)
        return Project(name=name,settings=SimulationSettings(80,64,.25,.5,5,2,'cpu'),objects=(SourceObject(name='Inclined line source',start=(16+24*math.sin(a),32-24*math.cos(a)),end=(16-24*math.sin(a),32+24*math.cos(a)),wavelength=4),MaterialObject(vertices=((40,0),(80,0),(80,64),(40,64)),refractive_index=1.5)),detectors=(DetectorObject(start=(50,24),end=(50,40),samples=129,settling=80,window=24),))
    return Project(name='Biconvex lens',settings=SimulationSettings(80,48,.1,.5,6,2,'cpu'),objects=(SourceObject(name='Finite line illumination',start=(12,7),end=(12,41),wavelength=.8),LensObject(x=30,y=24,radius=24,aperture=16)),detectors=(DetectorObject(start=(53,16),end=(53,32),samples=161,settling=80,window=16),))


def example(name):
    from importlib.resources import files
    from .persistence.projects import decode
    names={'Double slit':'double-slit','Refraction':'refraction','Biconvex lens':'biconvex-lens'}
    if name not in names:raise ValueError('Unknown example.')
    return decode(files('wave_studio').joinpath('data','examples',names[name]+'.wave.json').read_bytes())
