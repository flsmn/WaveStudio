"""Independent display ranges and toolbar/menu synchronization."""
from dataclasses import replace
import os

os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import pytest
from PySide6.QtWidgets import QApplication
from wave_studio.domain.project import Project
from wave_studio.persistence.projects import encode,decode
from wave_studio.ui.editor import MainWindow


@pytest.fixture
def window(tmp_path,monkeypatch):
    monkeypatch.setenv('WAVESTUDIO_RECOVERY_DIR',str(tmp_path))
    app=QApplication.instance() or QApplication([])
    window=MainWindow();window.show();app.processEvents()
    yield window
    window.lifecycle.dirty=False;window.close();app.processEvents()


def test_ranges_stay_independent_when_views_are_swapped(window,monkeypatch):
    import wave_studio.ui.editor as editor
    monkeypatch.setattr(editor,'compile_project',lambda *args:pytest.fail('display edit recompiled the scene'))
    window.secondary_toggle.click()
    window.lifecycle.run();identity=window.lifecycle.identity
    window.contrast.setValue(.75)
    window.intensity_range.setValue(.003)
    assert window.project.display.contrast==.75
    assert window.project.display.intensity_range==.003
    assert window.scale.levels()==(-.75,.75)
    assert window.second_scale.levels()==(0,.003)
    window.view.setCurrentText('Intensity');window.secondary_view.setCurrentText('Field')
    assert window.contrast.value()==.75 and window.intensity_range.value()==.003
    window.contrast.setValue(.5)
    assert window.scale.levels()==(0,.003)
    assert window.second_scale.levels()==(-.5,.5)
    window.intensity_range.setValue(.002)
    assert window.scale.levels()==(0,.002)
    assert window.second_scale.levels()==(-.5,.5)
    window.undo();assert window.intensity_range.value()==.003
    assert window.contrast.value()==.5
    window.redo();assert window.intensity_range.value()==.002
    assert window.lifecycle.identity==identity


def test_toolbar_second_view_syncs_with_menu_history_and_project(window):
    assert not window.secondary_toggle.isChecked()
    assert not window.secondary_view.isEnabled() and not window.second.isVisible()
    window.secondary_toggle.click()
    assert window.secondary_action.isChecked() and window.second.isVisible()
    assert window.secondary_view.isEnabled()
    window.secondary_view.setCurrentText('Field')
    window.secondary_toggle.click()
    assert not window.secondary_action.isChecked() and not window.second.isVisible()
    window.undo()
    assert window.secondary_toggle.isChecked() and window.second.isVisible()
    window.redo()
    assert not window.secondary_toggle.isChecked() and not window.second.isVisible()
    window.secondary_action.setChecked(True)
    assert window.secondary_toggle.isChecked() and window.second.isVisible()
    assert window.secondary_view.currentText()=='Field'
    changed=replace(window.project,display=replace(window.project.display,contrast=.8,intensity_range=.004))
    restored=decode(encode(changed));window.replace_project(restored)
    assert window.secondary_toggle.isChecked() and window.secondary_action.isChecked()
    assert window.contrast.value()==.8 and window.intensity_range.value()==.004
    window.replace_project(Project())
    assert not window.secondary_toggle.isChecked() and not window.secondary_action.isChecked()
    assert window.contrast.value()==.25 and window.intensity_range.value()==.0002
