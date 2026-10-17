"""Regression cases found during the Mac acceptance; software Qt, not native UI evidence."""
from dataclasses import replace
import math,os,time
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import pytest
from PySide6.QtWidgets import QApplication,QDialogButtonBox
from wave_studio.domain.project import Project,SourceObject,MaterialObject,WallObject,DetectorObject,SimulationSettings
from wave_studio.domain.quality import estimate,PRESETS,measures
from wave_studio.examples import example
from wave_studio.simulation.compiler import compile_project
from wave_studio.ui.dialogs import SettingsDialog,ObjectDialog
from wave_studio.ui.editor import MainWindow

@pytest.fixture
def window(tmp_path,monkeypatch):
    monkeypatch.setenv('WAVESTUDIO_RECOVERY_DIR',str(tmp_path))
    app=QApplication.instance() or QApplication([])
    w=MainWindow();w.show();app.processEvents()
    yield w
    w.lifecycle.dirty=False;w.close();app.processEvents()


def test_presets_long_path_rotated_structure_and_resource_rejection():
    angle=.51;c,s=math.cos(angle),math.sin(angle)
    vertices=tuple((30+x*c-y*s,8+x*s+y*c) for x,y in ((-3,-.1),(3,-.1),(3,.1),(-3,.1)))
    p=Project(settings=SimulationSettings(width=136,height=16,border_width=2),objects=(SourceObject(start=(4,8),wavelength=2),MaterialObject(vertices=vertices)),detectors=(DetectorObject(start=(132,8),end=None,samples=1),))
    assert measures(p)[2]==pytest.approx(.2) and measures(p)[3]==128
    for name,(_,features,budget) in PRESETS.items():
        e=estimate(p,name)
        assert e.phase_radians<=budget and e.cells_per_feature>=features
        if e.supported:compile_project(replace(p,settings=replace(p.settings,dx=e.dx)))
    lens=example('Biconvex lens')
    assert estimate(lens,'Preview').supported
    for name in ('Balanced','High Quality'):
        e=estimate(lens,name);assert not e.supported and 'MiB' in e.reason


def test_property_summary_and_reference_selection_survive_rebuild(window):
    w=window;source=w.project.objects[0];w.select_object(source.id)
    assert w.commit(replace(w.project,objects=(replace(source,wavelength=1.5),)))
    assert 'wavelength: 1.5' in w.properties.text()
    # A structural rebuild must not choose a different saved comparison.
    w.ref_combo.clear();w.ref_combo.addItem('No reference',-1);w.ref_combo.setCurrentIndex(0)
    w._rebuild_scene();assert w.ref_combo.currentData()==-1
    w.delete_selected();assert 'Select an object' in w.properties.text()


def test_paused_rates_remain_zero_after_acknowledgement(window):
    from wave_studio.simulation.worker import Frame
    w=window;w.lifecycle.run();w.lifecycle.pause();w._last_rate=time.monotonic()-2
    w.worker.latest.put(Frame(w.lifecycle.identity,1,240,None,paused=True))
    w._refresh_controls();w._poll()
    assert w.rate_label.text()=='0 steps/s · 0 frames/s'


def test_settings_keep_exact_preset_and_reject_without_project_change(window):
    w=window;p=example('Double slit');d=SettingsDialog(p,compile_project,w)
    d.quality.setCurrentText('High Quality');d.apply()
    assert d.result_project.settings.dx==estimate(p,'High Quality').dx
    d=SettingsDialog(p,compile_project,w);d.quality.setCurrentText('Balanced');d.boxes['dx'].setValue(.25)
    assert d.quality.currentText()=='Custom'
    p=example('Biconvex lens');d=SettingsDialog(p,compile_project,w);d.quality.setCurrentText('High Quality');d.apply()
    assert d.result_project is None and '512 MiB' in d.error.text()


def test_two_views_preserve_units_and_camera_on_display_change(window):
    w=window;w.secondary_action.setChecked(True);QApplication.processEvents()
    w.splitter.setSizes([250,500]);QApplication.processEvents()
    w.plot.setRange(xRange=(2,22),yRange=(4,24),padding=0);QApplication.processEvents()
    a,b=w.plot.getViewBox(),w.second.getViewBox()
    assert a.viewPixelSize()[0]==pytest.approx(b.viewPixelSize()[0],rel=.01)
    assert a.viewPixelSize()[0]==pytest.approx(a.viewPixelSize()[1],rel=.01)
    assert b.viewPixelSize()[0]==pytest.approx(b.viewPixelSize()[1],rel=.01)
    sizes=w.splitter.sizes();w.theme.setCurrentText('Light');assert w.splitter.sizes()==sizes
    w.second.setRange(xRange=(8,18),yRange=(8,18),padding=0);QApplication.processEvents()
    assert a.viewPixelSize()[0]==pytest.approx(b.viewPixelSize()[0],rel=.01)


def test_large_text_controls_and_dialog_buttons_stay_accessible(window,tmp_path):
    w=window;w.resize(980,660)
    for theme in ('Dark','Light'):
        for scale in (1.,1.25,1.5):
            assert w.commit(replace(w.project,display=replace(w.project.display,theme=theme,text_scale=scale)))
            QApplication.processEvents()
            for button in (w.run_button,w.pause_button,w.step_button,w.reset_button):
                assert w.centralWidget().rect().contains(button.mapTo(w.centralWidget(),button.rect().bottomRight()))
            assert w.run_button.font().pixelSize()==round(13*scale)
            w.grab().save(str(tmp_path/f'{theme}-{scale}.png'))
            d=ObjectDialog(DetectorObject(),lambda o:None,w);d.show();QApplication.processEvents()
            for button in d.findChild(QDialogButtonBox).buttons():assert d.rect().contains(button.mapTo(d,button.rect().bottomRight()))
            d.close()


def test_polygon_editor_tab_navigation_and_clear_invalid_shape(window):
    from PySide6.QtCore import Qt
    from PySide6.QtTest import QTest
    d=ObjectDialog(MaterialObject(),lambda o:None,window);d.show();QApplication.processEvents()
    editor=d.editors['vertices'];editor.setFocus();QTest.keyClick(editor,Qt.Key.Key_Tab)
    assert d.focusWidget() is not editor
    editor.setPlainText('5');d.apply()
    assert d.result_object is None and '[x, y]' in d.error.text()


def test_selected_lens_grip_is_above_overlapping_polygon(window):
    import pyqtgraph as pg
    from PySide6.QtCore import QPointF
    from wave_studio.domain.project import LensObject
    w=window;lens=LensObject(x=21,y=16)
    w.replace_project(Project(objects=(MaterialObject(),lens)))
    w.select_object(lens.id);QApplication.processEvents()
    target=next(item for item,_ in w.overlays if isinstance(item,pg.TargetItem))
    polygon=next(item for item,_ in w.overlays if isinstance(item,pg.PolyLineROI))
    assert target.zValue()>polygon.zValue()
    point=target.mapToScene(QPointF(0,0));items=w.plot.scene().items(point)
    assert items.index(target)<items.index(polygon)
