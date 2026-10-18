"""Color selection persists and recolors both panes without resetting results."""
from dataclasses import replace
import json
import os

os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import numpy as np
import pytest
from PySide6.QtGui import QImage
from PySide6.QtWidgets import QApplication
from wave_studio.domain.colors import FIELD_SCHEMES,INTENSITY_SCHEMES
from wave_studio.domain.project import Project
from wave_studio.persistence.projects import encode,decode
from wave_studio.simulation.worker import Frame
from wave_studio.ui.colors import color_map
from wave_studio.ui.editor import MainWindow


def test_schemes_roundtrip_and_legacy_defaults():
    project=Project()
    changed=replace(project,display=replace(project.display,field_scheme='Blue / Red',intensity_scheme='Inferno'))
    assert decode(encode(changed))==changed
    raw=json.loads(encode(changed))
    for name in ('field_scheme','intensity_scheme'):
        del raw['project']['display'][name]
    assert decode(json.dumps(raw)).display==project.display


@pytest.mark.parametrize('name,value',[('field_scheme','Viridis'),('intensity_scheme','Blue / Red'),('field_scheme',None)])
def test_unknown_scheme_is_rejected(name,value):
    project=Project()
    raw=json.loads(encode(project));raw['project']['display'][name]=value
    with pytest.raises(ValueError,match='color scheme'):
        decode(json.dumps(raw))


def test_color_controls_recolor_live_panes_and_preserve_results(tmp_path,monkeypatch):
    monkeypatch.setenv('WAVESTUDIO_RECOVERY_DIR',str(tmp_path/'recovery'))
    app=QApplication.instance() or QApplication([])
    window=MainWindow();window.show();app.processEvents()
    try:
        window.secondary_action.setChecked(True)
        scene=window.scene
        field=np.linspace(-.25,.25,np.prod(scene.grid.shape),dtype=np.float32).reshape(scene.grid.shape)
        intensity=field**2
        window.lifecycle.run()
        identity=window.lifecycle.identity
        frame=Frame(identity,1,10,field,intensity)
        window.frame=frame
        window._draw()
        for name,view,schemes,image,scale in (
            ('field_scheme','Field',FIELD_SCHEMES,window.image,window.scale),
            ('intensity_scheme','Intensity',INTENSITY_SCHEMES,window.second_image,window.second_scale),
        ):
            combo=window.color_combos[name]
            for scheme in schemes:
                combo.setCurrentText(scheme)
                expected=color_map(view,scheme)
                np.testing.assert_array_equal(image.lut,expected.getLookupTable(nPts=256,alpha=image.lut.shape[1]==4))
                assert scale.colorMap() is expected
                assert window.frame is frame and window.scene is scene
                assert window.lifecycle.identity==identity
            window.undo()
            assert combo.currentText()==schemes[-2]
            window.redo()
            assert combo.currentText()==schemes[-1]
        window.view.setCurrentText('Intensity');window.secondary_view.setCurrentText('Field')
        assert window.scale.colorMap() is color_map('Intensity','Grayscale')
        assert window.second_scale.colorMap() is color_map('Field','Grayscale')
        np.testing.assert_array_equal(window.image.image,intensity)
        np.testing.assert_array_equal(window.second_image.image,field)
        path=tmp_path/'view.png';window.write_png(path)
        metadata=json.loads(QImage(str(path)).text('wave-studio-metadata'))
        assert metadata['display']['field_scheme']=='Grayscale'
        assert metadata['display']['intensity_scheme']=='Grayscale'
        restored=decode(encode(window.project));window.replace_project(restored)
        assert all(combo.currentText()=='Grayscale' for combo in window.color_combos.values())
        window.replace_project(Project())
        assert all(combo.currentText()=='Classic' for combo in window.color_combos.values())
    finally:
        window.lifecycle.dirty=False;window.close();app.processEvents()
