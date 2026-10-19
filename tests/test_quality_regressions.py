"""Quality regressions; Qt checks are not native accessibility acceptance."""
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



def test_settings_keep_exact_preset_and_reject_without_project_change(window):
    w=window;p=example('Double slit');d=SettingsDialog(p,compile_project,w)
    d.quality.setCurrentText('High Quality');d.apply()
    assert d.result_project.settings.dx==estimate(p,'High Quality').dx
    d=SettingsDialog(p,compile_project,w);d.quality.setCurrentText('Balanced');d.boxes['dx'].setValue(.25)
    assert d.quality.currentText()=='Custom'
    p=example('Biconvex lens');d=SettingsDialog(p,compile_project,w);d.quality.setCurrentText('High Quality');d.apply()
    assert d.result_project is None and '512 MiB' in d.error.text()



def test_imported_preset_label_cannot_certify_a_coarse_grid():
    p=example('Refraction')
    with pytest.raises(ValueError,match='no longer meets'):
        compile_project(replace(p,settings=replace(p.settings,quality='High Quality',dx=.5)))



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
    for filename,scene in [('historical-slit-grids.json','Double slit'),('historical-lens-grids.json','Biconvex lens')]:
        report=json.loads((root/'tests/fixtures'/filename).read_text());assert report['passed']
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
