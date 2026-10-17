from dataclasses import asdict
import json
import math
import os
from pathlib import Path
import tempfile
from wave_studio.domain.project import (Project,SimulationSettings,DisplaySettings,SourceObject,MaterialObject,WallObject,LensObject,DetectorObject)
from wave_studio.simulation.compiler import compile_project

MAX_FILE_BYTES=8*1024**2
TYPES={c.__name__:c for c in (SourceObject,MaterialObject,WallObject,LensObject)}


def project_data(project):
    data=asdict(project)
    data['objects']=[{'type':type(o).__name__,**asdict(o)} for o in project.objects]
    return data


def physical_data(project):
    data=project_data(project)
    return json.loads(json.dumps({key:data[key] for key in ('id','name','reference_length','settings','objects')},allow_nan=False))


def _tuples(data):
    data=dict(data)
    for name in ('start','end'):
        if data.get(name) is not None: data[name]=tuple(data[name])
    if 'vertices' in data: data['vertices']=tuple(tuple(p) for p in data['vertices'])
    return data


def _finite_tree(value,depth=0):
    if depth>40: raise ValueError('Project nesting is too deep.')
    if isinstance(value,float) and not math.isfinite(value): raise ValueError('Project contains a non-finite number.')
    if isinstance(value,dict):
        for child in value.values(): _finite_tree(child,depth+1)
    if isinstance(value,list):
        if len(value)>20000: raise ValueError('Project array exceeds the size limit.')
        for child in value: _finite_tree(child,depth+1)


def validate_reference(ref):
    if not isinstance(ref,dict) or ref.get('status')!='complete': raise ValueError('Only completed reference profiles may be stored.')
    if not isinstance(ref.get('metadata'),dict) or not all(k in ref['metadata'] for k in ('scene','run_id','engine_version','grid','dt','backend','dtype','time')): raise ValueError('Reference origin metadata is missing.')
    values,axis,positions=ref.get('values'),ref.get('axis'),ref.get('positions')
    if not isinstance(values,list) or not 1<=len(values)<=2048 or not isinstance(axis,list) or len(axis)!=len(values) or not isinstance(positions,list) or len(positions)!=len(values): raise ValueError('Reference profile dimensions are invalid.')
    if any(isinstance(v,bool) or not isinstance(v,(int,float)) or v<0 for v in values): raise ValueError('Reference intensities must be nonnegative numbers.')
    if any(not isinstance(p,list) or len(p)!=2 or any(not isinstance(v,(int,float)) for v in p) for p in positions): raise ValueError('Reference coordinates are invalid.')
    if any(not isinstance(v,(int,float)) for v in axis) or any(b<a for a,b in zip(axis,axis[1:])): raise ValueError('Reference axis must be ordered.')
    if ref.get('duration',0)<=0 or ref.get('sample_count',0)<1: raise ValueError('Reference measurement metadata is invalid.')


def from_data(data):
    try:
        _finite_tree(data)
        data=dict(data)
        objects=[]
        for raw in data.pop('objects'):
            raw=dict(raw); cls=TYPES[raw.pop('type')]; objects.append(cls(**_tuples(raw)))
        data['objects']=tuple(objects)
        data['settings']=SimulationSettings(**data['settings'])
        data['display']=DisplaySettings(**data['display'])
        data['detectors']=tuple(DetectorObject(**_tuples(d)) for d in data.get('detectors',[]))
        data['references']=tuple(data.get('references',[]))
        for ref in data['references']: validate_reference(ref)
        project=Project(**data).validate()
        compile_project(project)
        return project
    except (KeyError,TypeError,AttributeError,OverflowError) as error:
        raise ValueError(f'Invalid project content: {error}') from error


def encode(project):
    project.validate()
    for reference in project.references: validate_reference(reference)
    result=json.dumps({'format':'wave-studio','version':1,'project':project_data(project)},indent=2,allow_nan=False).encode('utf8')
    if len(result)>MAX_FILE_BYTES: raise ValueError('Project exceeds the 8 MiB file limit.')
    return result


def decode(raw):
    if len(raw)>MAX_FILE_BYTES: raise ValueError('Project exceeds the 8 MiB file limit.')
    try:
        data=json.loads(raw)
        if data.get('format')!='wave-studio' or type(data.get('version')) is not int or data['version']!=1: raise ValueError('Unsupported Wave Studio project version.')
        return from_data(data['project'])
    except (json.JSONDecodeError,UnicodeDecodeError,TypeError,AttributeError,KeyError) as error:
        raise ValueError(f'Cannot read project: {error}') from error


def atomic_write(path,content):
    path=Path(path)
    temp=None
    try:
        with tempfile.NamedTemporaryFile(dir=path.parent,prefix='.'+path.name,suffix='.tmp',delete=False) as stream:
            temp=Path(stream.name)
            stream.write(content)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temp,path)
    finally:
        if temp is not None and temp.exists(): temp.unlink()


def save(path,project): atomic_write(path,encode(project))
def load(path):
    with Path(path).open('rb') as stream: return decode(stream.read(MAX_FILE_BYTES+1))
