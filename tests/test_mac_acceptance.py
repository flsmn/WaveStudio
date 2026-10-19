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
    w=window;w.lifecycle.run();w._rates.observe(1,time.monotonic()-2);w.lifecycle.pause()
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


def test_mac_standard_shortcuts_route_to_history_and_run(window):
    from PySide6.QtCore import Qt
    from PySide6.QtGui import QKeySequence
    from PySide6.QtTest import QTest
    from wave_studio.simulation.lifecycle import State
    w=window;source=w.project.objects[0]
    w.activateWindow();w.setFocus();QApplication.processEvents()
    w.commit(replace(w.project,objects=(replace(source,wavelength=1.5),)))
    QTest.keySequence(w,QKeySequence(QKeySequence.StandardKey.Undo));QApplication.processEvents()
    assert w.project.objects[0].wavelength==2
    QTest.keySequence(w,QKeySequence(QKeySequence.StandardKey.Redo));QApplication.processEvents()
    assert w.project.objects[0].wavelength==1.5
    QTest.keySequence(w,QKeySequence('Ctrl+R'));QTest.qWait(150);QApplication.processEvents()
    assert w.lifecycle.state==State.RUNNING
    w.pause_simulation()


def test_geometric_tools_convert_screen_points_at_two_zoom_levels(window):
    from PySide6.QtCore import Qt,QPointF
    w=window
    class Event:
        def __init__(self,p):self.p=p
        def button(self):return Qt.MouseButton.LeftButton
        def scenePos(self):return w.plot.getViewBox().mapViewToScene(QPointF(*self.p))
    for extent in (32,16):
        w.plot.setRange(xRange=(0,extent),yRange=(0,extent),padding=0);QApplication.processEvents()
        w.start_measure('distance')
        for point in ((3,4),(6,8)):w.canvas_click(Event(point))
        assert w.message.text()=='Distance: 5.00000 reference lengths'
        w.start_measure('angle')
        for point in ((3,4),(6,4),(6,8)):w.canvas_click(Event(point))
        assert w.message.text()=='Angle: 90.000°'


def test_imported_preset_label_cannot_certify_a_coarse_grid():
    p=example('Refraction')
    with pytest.raises(ValueError,match='no longer meets'):
        compile_project(replace(p,settings=replace(p.settings,quality='High Quality',dx=.5)))


def test_save_and_discard_supersede_only_own_recovery(window,tmp_path,monkeypatch):
    from PySide6.QtWidgets import QMessageBox
    from wave_studio.persistence.projects import save,load
    w=window;w.path=tmp_path/'saved.wave.json'
    w.lifecycle.dirty=True;w._recover_save();assert w.recovery.exists()
    assert w.save_project() and not w.recovery.exists()
    w.lifecycle.dirty=True;w._recover_save()
    monkeypatch.setattr(QMessageBox,'question',lambda *a:QMessageBox.StandardButton.Discard)
    assert w.confirm_discard() and not w.recovery.exists()
    other=Project(name='Other experiment');save(w.recovery,other)
    assert w.confirm_discard() and load(w.recovery)==other
    w.recovery.unlink()


@pytest.mark.parametrize('focus',['plot','tree'])
def test_history_shortcut_while_canvas_or_tree_focused(window,focus):
    from PySide6.QtGui import QKeySequence
    from PySide6.QtTest import QTest
    w=window;source=w.project.objects[0]
    w.commit(replace(w.project,objects=(replace(source,wavelength=1.5),)))
    target=getattr(w,focus);w.activateWindow();target.setFocus();QApplication.processEvents()
    QTest.keySequence(target,QKeySequence(QKeySequence.StandardKey.Undo));QApplication.processEvents()
    assert w.project.objects[0].wavelength==2


def test_large_text_minimum_window_with_two_views_and_long_counters(window):
    w=window
    w.commit(replace(w.project,display=replace(w.project.display,text_scale=1.5,secondary_visible=True,theme='Light')))
    w.time_label.setText('t = 1284.250 · 20,548 steps');w.state_label.setText('Paused')
    w.resize(980,660);QApplication.processEvents()
    assert w.size().width()==980 and w.size().height()==660
    for chart in (w.plot,w.second,w.profile_plot):
        assert chart.getAxis('bottom').labelStyle['color']=='#42566b'
    for chart in (w.plot,w.second):
        assert chart.getAxis('bottom').labelText=='x' and chart.getAxis('left').labelText=='y'
        assert chart.getAxis('bottom').labelUnits==chart.getAxis('left').labelUnits=='reference length'
    assert w.profile_plot.getPlotItem().legend.opts['labelTextColor']=='#42566b'
    from wave_studio.simulation.lifecycle import State
    w.state_label.setText(State.CHANGED.value);QApplication.processEvents()
    for label in (w.state_label,w.time_label,w.rate_label):
        assert w.centralWidget().rect().contains(label.mapTo(w.centralWidget(),label.rect().bottomRight()))


def test_material_order_history_and_copy_delete_preserve_stopped_state(window):
    from wave_studio.simulation.lifecycle import State
    a,b=MaterialObject(name='First',refractive_index=1.2),MaterialObject(name='Second',refractive_index=2)
    w=window;w.replace_project(Project(objects=(a,b)));w.select_object(a.id)
    assert w.scene.refractive_index[128,160]==2
    w.reorder(1);assert w.scene.refractive_index[128,160]==pytest.approx(1.2)
    w.undo();assert w.scene.refractive_index[128,160]==2
    w.redo();assert w.scene.refractive_index[128,160]==pytest.approx(1.2)
    w.duplicate_selected();assert len(w.project.objects)==3
    w.delete_selected();assert len(w.project.objects)==2
    assert w.lifecycle.state==State.CHANGED and not w.lifecycle.can_step


def test_scene_updates_preserve_outline_rows_and_keyboard_focus(window):
    from PySide6.QtCore import Qt
    w=window;source=w.project.objects[0];w.select_object(source.id);row=w.tree.topLevelItem(0)
    w.tree.setFocus();QApplication.processEvents()
    w.commit(replace(w.project,objects=(replace(source,name='Renamed',wavelength=1.5),)))
    assert w.tree.topLevelItem(0) is row and row.text(0)=='Renamed'
    assert w.tree.hasFocus()
    extra=MaterialObject();w.commit(replace(w.project,objects=w.project.objects+(extra,)))
    assert w.tree.topLevelItem(0) is row and w.tree.topLevelItemCount()==2
    w.selected=extra.id;w._rebuild_scene();w.delete_selected()
    assert w.tree.topLevelItem(0) is row and w.tree.topLevelItemCount()==1


def test_scene_edits_do_not_repolish_the_native_outline(window,monkeypatch):
    w=window;source=w.project.objects[0];w.select_object(source.id)
    row=w.tree.topLevelItem(0);calls=[];apply=w._apply_theme
    def record(theme):
        calls.append(theme);apply(theme)
    monkeypatch.setattr(w,'_apply_theme',record)
    assert w.commit(replace(w.project,objects=(replace(source,amplitude=1.1),)))
    w.undo();w.redo()
    assert calls==[] and w.tree.topLevelItem(0) is row
    assert w.commit(replace(w.project,display=replace(w.project.display,contrast=.5)))
    assert calls==[]
    assert w.commit(replace(w.project,display=replace(w.project.display,text_scale=1.5)))
    assert calls==[w.project.display.theme]
    theme='Light' if w.project.display.theme=='Dark' else 'Dark'
    assert w.commit(replace(w.project,display=replace(w.project.display,theme=theme)))
    assert calls[-1]==theme and len(calls)==2


def test_scene_rename_add_remove_history_preserves_selection_and_stopped_state(window):
    w=window;original=w.project.objects[0];w.select_object(original.id)
    extra=SourceObject(name='Added source');w.selected=extra.id
    assert w.commit(replace(w.project,objects=w.project.objects+(extra,)))
    assert w.tree.topLevelItemCount()==2 and w.selected==extra.id
    assert w.commit(replace(w.project,objects=(original,replace(extra,name='Renamed source'))))
    assert w.tree.topLevelItem(1).text(0)=='Renamed source'
    w.undo();assert w.tree.topLevelItem(1).text(0)=='Added source'
    w.undo();assert w.tree.topLevelItemCount()==1 and w.selected is None
    w.redo();assert w.tree.topLevelItemCount()==2
    w.selected=extra.id;w._rebuild_scene();w.delete_selected()
    assert w.tree.topLevelItemCount()==1 and w.selected is None
    assert not w.lifecycle.can_step


def test_presets_avoid_half_open_wall_ties_and_warn_for_custom(window):
    from wave_studio.domain.quality import wall_cell_ties
    p=example('Double slit');assert wall_cell_ties(p,.2)
    for name in PRESETS:assert not wall_cell_ties(p,estimate(p,name).dx)
    window.replace_project(replace(p,settings=replace(p.settings,dx=.2)))
    assert 'half-open tie rule' in window.warning.text()


def test_historical_physical_acceptance_grids_meet_their_numerical_criteria():
    import json
    from pathlib import Path
    root=Path(__file__).resolve().parents[1]
    for filename,scene in [('quality-slit-results.json','Double slit'),('quality-lens-results.json','Biconvex lens')]:
        report=json.loads((root/'docs'/filename).read_text());assert report['passed']
        for result in report['cases']:
            if result['name'] not in PRESETS:continue
            # These reports predate the visual raster floors. Keep their measured
            # grids and numerical criteria; they do not certify the new presets.
            selected=estimate(example(scene),result['name'],result['dx'])
            assert result['grid']==[selected.nx,selected.ny] and result['dx']==selected.dx
            waves,features,budget=PRESETS[result['name']]
            assert selected.cells_per_wavelength>=waves
            assert selected.cells_per_feature is None or selected.cells_per_feature>=features
            assert selected.phase_radians<=budget


def test_completed_profile_redraws_only_when_visible_data_changes(window,monkeypatch):
    import torch
    from wave_sim2d.measurements import Measurements
    w=window;d=DetectorObject(samples=2,settling=0,window=1)
    w.replace_project(Project(detectors=(d,)))
    measurements=Measurements(w.scene.grid,'cpu');measurements.configure(w.detector_specs(),0)
    field=torch.ones(w.scene.grid.shape)
    for i in range(16):measurements.update(field,(i+1)*w.scene.grid.dt,w.scene.grid.dt)
    profile=measurements.results()[d.id];w.profiles[d.id]=profile;w._plot_profiles()
    clears=[];original=w.profile_plot.clear
    def clear():clears.append(1);original()
    monkeypatch.setattr(w.profile_plot,'clear',clear)
    for _ in range(10):w._plot_profiles()
    assert clears==[]
    w.profiles[d.id]={**profile,'metadata':{'time':99}};w._plot_profiles();assert clears==[]
    w.profiles[d.id]={**profile,'values':[.25,.5]};w._plot_profiles();assert len(clears)==1
    w.norm.setCurrentText('Shared maximum = 1');assert len(clears)==2
    w.theme.setCurrentText('Light');assert len(clears)==3
