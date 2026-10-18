"""Probe quantity switching, signed live samples and frozen field references."""
from copy import deepcopy
from dataclasses import replace
import csv,json,os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import numpy as np
import pytest
import torch
from PySide6.QtWidgets import QApplication
from wave_sim2d.measurements import Measurements
from wave_studio.domain.project import Project,DetectorObject
from wave_studio.persistence.projects import encode,decode
from wave_studio.persistence.exports import export_csv
from wave_studio.ui.editor import MainWindow


@pytest.fixture
def probe(tmp_path,monkeypatch):
    monkeypatch.setenv('WAVESTUDIO_RECOVERY_DIR',str(tmp_path/'recovery'))
    app=QApplication.instance() or QApplication([])
    window=MainWindow();window.show();app.processEvents()
    detector=DetectorObject(start=(10,10),end=(12,10),samples=3,settling=0,window=window.scene.grid.dt)
    window.replace_project(Project(detectors=(detector,)))
    measurements=Measurements(window.scene.grid,'cpu');measurements.configure(window.detector_specs(),0)
    grid=window.scene.grid
    field=(2*((torch.arange(grid.nx)+.5)*grid.dx-11)).repeat(grid.ny,1)
    measurements.update(field,grid.dt,grid.dt)
    window.profiles[detector.id]={**measurements.results()[detector.id],'metadata':window.metadata()}
    window._plot_profiles()
    yield window,detector,measurements,field
    window.lifecycle.dirty=False;window.close();app.processEvents()


def test_switching_to_signed_live_field_preserves_intensity_and_running_identity(probe):
    window,detector,measurements,field=probe
    intensity=window.profiles[detector.id]['values'][:]
    window.lifecycle.run();identity=window.lifecycle.identity;scene=window.scene
    window.probe_view.setCurrentText('Field')
    np.testing.assert_allclose(window.profile_plot.listDataItems()[0].getData()[1],[-2,0,2])
    assert window.profile_plot.getAxis('left').labelText=='Field (instantaneous, relative)'
    assert 'Live field' in window.profile_status.text()
    window.norm.setCurrentIndex(1)
    np.testing.assert_allclose(window.profile_plot.listDataItems()[0].getData()[1],[-1,0,1])
    assert window.profiles[detector.id]['field_values']==[-2,0,2]
    grid=scene.grid;measurements.update(-3*field,2*grid.dt,grid.dt)
    window.profiles[detector.id]={**measurements.results()[detector.id],'metadata':window.metadata()}
    window.norm.setCurrentIndex(0);window._plot_profiles()
    np.testing.assert_allclose(window.profile_plot.listDataItems()[0].getData()[1],[6,0,-6])
    window.probe_view.setCurrentText('Intensity')
    np.testing.assert_allclose(window.profile_plot.listDataItems()[0].getData()[1],intensity)
    assert window.lifecycle.identity==identity and window.scene is scene
    assert window.profiles[detector.id]['values']==intensity
    window.undo();assert window.probe_view.currentText()=='Field'
    window.redo();assert window.probe_view.currentText()=='Intensity'


def test_field_reference_freezes_snapshot_and_exports_signed_raw_values(probe,tmp_path):
    window,detector,measurements,field=probe
    window.probe_view.setCurrentText('Field');window.hold_reference()
    reference=deepcopy(window.project.references[0])
    grid=window.scene.grid;measurements.update(3*field,2*grid.dt,grid.dt)
    window.profiles[detector.id]={**measurements.results()[detector.id],'metadata':window.metadata()}
    window._plot_profiles()
    assert window.project.references[0]==reference
    np.testing.assert_allclose(window.profile_plot.listDataItems()[1].getData()[1],[-2,0,2])
    restored=decode(encode(window.project))
    assert restored.display.probe_view=='Field' and restored.references[0]==reference
    path=tmp_path/'field.csv';export_csv(path,reference,quantity='Field')
    lines=path.read_text().splitlines()
    rows=list(csv.DictReader(line for line in lines if not line.startswith('#')))
    assert [float(row['relative_field']) for row in rows]==[-2,0,2]
    metadata=json.loads(lines[1].removeprefix('# metadata: '))
    assert metadata['quantity']=='Field' and metadata['time']==reference['field_time']
    assert window.project.references[0]==reference
    window.replace_project(restored);assert window.probe_view.currentText()=='Field'


def test_old_intensity_only_references_are_not_presented_as_field(probe):
    window,detector,measurements,field=probe
    window.hold_reference();legacy=deepcopy(window.project.references[0])
    del legacy['field_values'];del legacy['field_time']
    project=replace(window.project,references=(legacy,),display=replace(window.project.display,probe_view='Field'))
    window.replace_project(decode(encode(project)));window.ref_combo.setCurrentIndex(1)
    assert not window.profile_plot.listDataItems()
    assert 'intensity only' in window.profile_status.text()
    raw=json.loads(encode(project));del raw['project']['display']['probe_view']
    assert decode(json.dumps(raw)).display.probe_view=='Intensity'


@pytest.mark.parametrize('values,time',[([-2,0],.5),([-2,float('nan'),2],.5),([-2,0,2],-1)])
def test_malformed_field_reference_is_rejected(probe,values,time):
    window,detector,measurements,field=probe
    window.hold_reference();reference=deepcopy(window.project.references[0])
    reference.update(field_values=values,field_time=time)
    with pytest.raises(ValueError):encode(replace(window.project,references=(reference,)))
