"""Editor regressions; Qt checks are not native accessibility acceptance."""
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


def test_property_summary_and_reference_selection_survive_rebuild(window):
    w=window;source=w.project.objects[0];w.select_object(source.id)
    assert w.commit(replace(w.project,objects=(replace(source,wavelength=1.5),)))
    assert 'wavelength: 1.5' in w.properties.text()
    # A structural rebuild must not choose a different saved comparison.
    w.ref_combo.clear();w.ref_combo.addItem('No reference',-1);w.ref_combo.setCurrentIndex(0)
    w._rebuild_scene();assert w.ref_combo.currentData()==-1
    w.delete_selected();assert 'Select an object' in w.properties.text()



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
