"""Domain dimensions above 100 must survive editing and reopening settings."""
from dataclasses import replace
import os

os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import pytest
from PySide6.QtWidgets import QApplication
from wave_studio.domain.project import Project
from wave_studio.persistence.projects import encode,decode
from wave_studio.ui.dialogs import SettingsDialog


@pytest.mark.parametrize('width,height,dx',[(150,125,1),(10000,10000,100)])
def test_large_dimensions_apply_roundtrip_and_reopen(width,height,dx):
    app=QApplication.instance() or QApplication([])
    project=Project()
    project=replace(project,settings=replace(project.settings,quality='Custom',dx=dx),
                    objects=(replace(project.objects[0],start=(width/2,height/2)),))
    dialog=SettingsDialog(project,lambda p:p.validate())
    try:
        dialog.boxes['width'].setValue(width)
        dialog.boxes['height'].setValue(height)
        dialog.apply()
        assert dialog.result_project is not None,dialog.error.text()
        restored=decode(encode(dialog.result_project))
        assert (restored.settings.width,restored.settings.height)==(width,height)
        reopened=SettingsDialog(restored,lambda p:p.validate())
        try:
            assert reopened.boxes['width'].value()==width
            assert reopened.boxes['height'].value()==height
            reopened.apply()
            assert reopened.result_project==restored
        finally:
            reopened.close()
    finally:
        dialog.close()


def test_large_domain_still_obeys_resource_limits():
    app=QApplication.instance() or QApplication([])
    project=Project()
    project=replace(project,settings=replace(project.settings,quality='Custom',dx=.125))
    dialog=SettingsDialog(project,lambda p:p.validate())
    try:
        dialog.boxes['width'].setValue(1000)
        dialog.boxes['height'].setValue(1000)
        dialog.apply()
        assert dialog.result_project is None
        assert 'configured limits' in dialog.error.text()
    finally:
        dialog.close()
