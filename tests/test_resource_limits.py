from dataclasses import replace
import json,os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import pytest
from PySide6.QtWidgets import QApplication
from wave_studio.domain.project import Project
from wave_studio.domain.quality import estimate
from wave_studio.domain.history import change_kind
from wave_studio.examples import example
from wave_studio.persistence.projects import encode,decode
from wave_studio.simulation.compiler import compile_project
from wave_studio.ui.dialogs import SettingsDialog
from wave_studio.ui.editor import MainWindow


def test_configured_budgets_admit_balanced_and_high_without_changing_quality(monkeypatch):
    import wave_studio.simulation.compiler as compiler
    p=example('Biconvex lens');baseline=estimate(p,'Balanced')
    assert not baseline.supported
    p=replace(p,settings=replace(p.settings,buffer_limit_mib=768))
    e=estimate(p,'Balanced');assert e.supported and e.dx==baseline.dx
    # Admission/propagation without allocating millions of cells in unit tests.
    monkeypatch.setattr(compiler,'prepare_scene',lambda grid,*args:grid)
    g=compile_project(replace(p,settings=replace(p.settings,quality='Balanced',dx=e.dx)))
    assert (g.nx,g.ny)==(3780,2268) and g.estimated_bytes==617258880
    p=replace(p,settings=replace(p.settings,buffer_limit_mib=1536))
    assert not estimate(p,'High Quality').supported
    p=replace(p,settings=replace(p.settings,max_axis_cells=8192))
    e=estimate(p,'High Quality');assert e.supported
    g=compile_project(replace(p,settings=replace(p.settings,quality='High Quality',dx=e.dx)))
    assert (g.nx,g.ny,g.max_axis_cells)==(5665,3399,8192)


def test_custom_budget_rejected_before_any_raster_allocation(monkeypatch):
    import wave_studio.simulation.compiler as compiler
    monkeypatch.setattr(compiler,'prepare_scene',lambda *args:pytest.fail('allocated an oversized scene'))
    p=Project()
    for settings in (replace(p.settings,buffer_limit_mib=1),replace(p.settings,max_axis_cells=128)):
        with pytest.raises(ValueError,match='configured limits'):compile_project(replace(p,settings=settings))


@pytest.mark.parametrize('name,value',[('buffer_limit_mib',0),('buffer_limit_mib',True),('buffer_limit_mib',768.0),('buffer_limit_mib',65537),('max_axis_cells',7),('max_axis_cells',False),('max_axis_cells',float('nan'))])
def test_invalid_imported_limits_rejected(name,value):
    with pytest.raises(ValueError):replace(Project(),settings=replace(Project().settings,**{name:value})).validate()


def test_limits_roundtrip_legacy_defaults_and_nonphysical_classification():
    p=Project();other=replace(p,settings=replace(p.settings,buffer_limit_mib=768,max_axis_cells=8192))
    assert decode(encode(other))==other and change_kind(p,other)=='display'
    raw=json.loads(encode(p));raw['project']['settings'].pop('buffer_limit_mib');raw['project']['settings'].pop('max_axis_cells')
    assert decode(json.dumps(raw)).settings==p.settings


def test_dialog_rechecks_budgets_and_preserves_preset():
    app=QApplication.instance() or QApplication([])
    p=example('Biconvex lens');d=SettingsDialog(p,lambda p:p.validate());d.show();app.processEvents()
    try:
        d.quality.setCurrentText('Balanced');d.apply()
        assert d.result_project is None and '512 MiB' in d.error.text()
        d.boxes['buffer_limit_mib'].setValue(768)
        assert d.quality.currentText()=='Balanced' and 'Large grid' in d.error.text()
        d.apply();candidate=d.result_project
        assert candidate.settings.quality=='Balanced' and candidate.settings.buffer_limit_mib==768
        assert candidate.settings.dx==estimate(candidate,'Balanced').dx
    finally:d.close()


def test_budget_edits_preserve_run_and_run_reuses_prepared_scene(tmp_path,monkeypatch):
    from PySide6.QtTest import QTest
    from time import monotonic
    import torch
    from wave_studio.simulation.lifecycle import State
    import wave_studio.ui.editor as editor
    monkeypatch.setenv('WAVESTUDIO_RECOVERY_DIR',str(tmp_path))
    app=QApplication.instance() or QApplication([]);w=MainWindow();w.show()
    torch.set_num_threads(1)
    def wait_for(condition):
        deadline=monotonic()+3
        while not condition() and monotonic()<deadline:QTest.qWait(10)
        assert condition()
    try:
        monkeypatch.setattr(editor,'compile_project',lambda *args:pytest.fail('Run re-rasterized the scene'))
        w.run_simulation();wait_for(lambda:w.frame is not None and w.frame.steps>0)
        w.pause_simulation();wait_for(lambda:w.frame.paused)
        identity=w.lifecycle.identity;scene=w.scene;frame=w.frame
        assert w.commit(replace(w.project,settings=replace(w.project.settings,buffer_limit_mib=768)))
        assert w.lifecycle.identity==identity and w.lifecycle.state==State.PAUSED and w.frame is frame and w.scene is scene
        assert not w.commit(replace(w.project,settings=replace(w.project.settings,buffer_limit_mib=1)))
        assert w.project.settings.buffer_limit_mib==768 and w.frame is frame
        w.run_simulation();wait_for(lambda:w.frame.steps>frame.steps)
        assert w.lifecycle.identity==identity and w.frame.steps>frame.steps
    finally:w.lifecycle.dirty=False;w.close();app.processEvents()


def test_large_images_downsample_only_rendering_and_retain_full_grid(tmp_path,monkeypatch):
    import numpy as np
    from wave_studio.domain.project import SimulationSettings
    monkeypatch.setenv('WAVESTUDIO_RECOVERY_DIR',str(tmp_path))
    app=QApplication.instance() or QApplication([]);w=MainWindow();w.resize(980,660);w.show()
    try:
        p=Project(settings=SimulationSettings(dx=1/32))
        p=replace(p,display=replace(p.display,view='Material',secondary_view='Material',secondary_visible=True))
        w.replace_project(p);app.processEvents()
        for image in (w.image,w.second_image):
            image.render()
            assert image.autoDownsample and image.image.shape==(1024,1024)
            assert np.shares_memory(image.image,w.scene.refractive_index)
            assert max(image.qimage.width(),image.qimage.height())<1024
        from wave_studio.simulation.worker import Frame
        w.commit(replace(w.project,display=replace(w.project.display,view='Field')))
        for shape,preview in (((32,32),True),((1024,1024),False)):
            w.frame=Frame(w.lifecycle.identity,1,1,np.zeros(shape,dtype=np.float32),preview=preview)
            w._draw()
            rect=w.image.mapRectToParent(w.image.boundingRect())
            assert (rect.x(),rect.y(),rect.width(),rect.height())==(0,0,32,32)
            assert w.metadata()['display_preview']==preview and w.metadata()['display_shape']==list(shape)
    finally:w.lifecycle.dirty=False;w.close();app.processEvents()
