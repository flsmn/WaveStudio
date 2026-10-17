from dataclasses import replace
from copy import deepcopy
import json
import numpy as np
import pytest
from wave_studio.domain.project import Project,DetectorObject,LensObject,MaterialObject
from wave_studio.domain.history import History,change_kind
from wave_studio.examples import example
from wave_studio.persistence.projects import encode,decode,load,save
from wave_studio.persistence.exports import export_csv


def reference():
    from wave_studio.persistence.projects import physical_data
    return {'status':'complete','detector_id':'d','measurement_revision':0,'begin':1,'duration':2,'elapsed':2,'sample_count':16,'axis':[0,1],'positions':[[2,3],[2,4]],'values':[.1,.2],'metadata':{'scene':physical_data(Project()),'run_id':'run','engine_version':'0.1.0.dev1','grid':{'nx':32},'dt':.1,'backend':'cpu','dtype':'float32','time':3}}


def test_roundtrip_examples_and_frozen_reference(tmp_path):
    for name in ('Double slit','Refraction','Biconvex lens'):
        project=replace(example(name),references=(reference(),))
        assert decode(encode(project))==project
        path=tmp_path/'project.wave.json';save(path,project);assert load(path)==project
    profile=reference();before=deepcopy(profile)
    export_csv(tmp_path/'profile.csv',profile)
    assert profile==before
    rows=[r for r in (tmp_path/'profile.csv').read_text().splitlines() if not r.startswith('#')]
    import csv
    values=list(csv.DictReader(rows))
    assert float(values[1]['relative_mean_field_squared'])==.2


def test_invalid_open_and_failed_write_preserve_valid_file(tmp_path,monkeypatch):
    path=tmp_path/'project.wave.json';original=Project();save(path,original)
    import wave_studio.persistence.projects as files
    with monkeypatch.context() as m:
        m.setattr(files.os,'replace',lambda *args:(_ for _ in ()).throw(OSError('disk failure')))
        with pytest.raises(OSError): save(path,replace(original,name='Changed'))
    assert load(path)==original
    assert len(list(tmp_path.iterdir()))==1
    data=json.loads(encode(original));data['version']=99
    with pytest.raises(ValueError):decode(json.dumps(data))
    with pytest.raises(ValueError):decode(b'{bad json')
    data=json.loads(encode(original));data['project']['objects'][0]['wavelength']=-1
    with pytest.raises(ValueError):decode(json.dumps(data))
    data=json.loads(encode(original));data['project']['references']=[reference()];data['project']['references'][0]['values']=[1]
    with pytest.raises(ValueError):decode(json.dumps(data))


def test_undo_change_classes_and_lens_contour():
    p=Project();history=History();changed=replace(p,detectors=(DetectorObject(),))
    assert change_kind(p,changed)=='measurement'
    history.push(p,changed);assert history.undo()==p;assert history.redo()==changed
    display=replace(changed,display=replace(changed.display,view='Intensity'))
    assert change_kind(changed,display)=='display'
    from wave_sim2d.geometry import lens_vertices
    contour=lens_vertices(30,24,24,16)
    thickness=2*(24-np.sqrt(24**2-8**2))
    assert max(x for x,y in contour)-min(x for x,y in contour)==pytest.approx(thickness)
