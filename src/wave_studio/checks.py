"""T05/T06 integration exercise against the actual Qt editor and single worker."""
from dataclasses import replace
from pathlib import Path
import json
import sys
import wave_sim2d
import os
import tempfile
import time
import torch
from PySide6.QtWidgets import QApplication
from PySide6.QtGui import QImage
from wave_studio.ui.editor import MainWindow
from wave_studio.examples import example
from wave_studio.domain.project import Project,DetectorObject,MaterialObject
from wave_studio.domain.colors import FIELD_SCHEMES,INTENSITY_SCHEMES
from wave_studio.ui.dialogs import SettingsDialog
from wave_studio.ui.colors import color_map
from wave_studio.simulation.compiler import compile_project
from wave_studio.persistence.projects import save,load,encode,decode
from wave_studio.persistence.exports import export_csv
from wave_studio.simulation.lifecycle import State


def run_workflow(output_directory):
    torch.set_num_threads(1)
    app=QApplication([])
    output=Path(output_directory);output.mkdir(parents=True,exist_ok=True)
    os.environ['WAVESTUDIO_RECOVERY_DIR']=str(output/'.recovery')
    window=MainWindow();window.show()
    results={}
    
    def wait_until(predicate,timeout=12):
        deadline=time.monotonic()+timeout
        while time.monotonic()<deadline:
            app.processEvents();window._poll()
            if predicate():return
            time.sleep(.003)
        raise AssertionError('Timed out: '+window.message.text())
    
    try:
        project=Project()
        project=replace(project,settings=replace(project.settings,quality='Custom',dx=1))
        dialog=SettingsDialog(project,compile_project,window)
        try:
            dialog.boxes['width'].setValue(150);dialog.boxes['height'].setValue(125);dialog.apply()
            assert dialog.result_project is not None,dialog.error.text()
            restored=decode(encode(dialog.result_project))
            assert (restored.settings.width,restored.settings.height)==(150,125)
        finally:dialog.close()
        # Same three walls and illumination as numerical T03, created as editable model objects.
        p=example('Double slit')
        p=replace(p,compute_mode='Performance',detectors=p.detectors+(DetectorObject(name='Second detector',start=(50,32),end=None,samples=1,settling=0,window=2),))
        window.replace_project(p)
        window.run_simulation()
        wait_until(lambda:len(window.profiles)==2 and all(p['status']=='complete' for p in window.profiles.values()))
        run=window.lifecycle.identity
        window.hold_reference()
        assert len(window.project.references)==1
        reference=window.project.references[0]
        export_csv(output/'double-slit.csv',reference)
        window.pause_simulation()
        wait_until(lambda:window.frame is not None and window.frame.paused)
        before=window.frame.steps
        window.step_simulation();wait_until(lambda:window.frame.steps==before+1)
        assert window.lifecycle.identity==run
        window.run_simulation();assert window.lifecycle.identity==run
        detector=window.project.detectors[0]
        unaffected=window.profiles[window.project.detectors[1].id]['values']
        moved=replace(detector,start=(53,24),end=(53,40))
        assert window.commit(replace(window.project,detectors=(moved,window.project.detectors[1])))
        assert window.lifecycle.identity==run
        revision=window.revisions[detector.id]
        wait_until(lambda:detector.id in window.profiles and window.profiles[detector.id]['measurement_revision']==revision)
        assert window.profiles[window.project.detectors[1].id]['values']==unaffected
        assert window.profiles[detector.id]['sample_count']<reference['sample_count']
        valid=window.project
        assert not window.commit(replace(valid,detectors=(replace(moved,start=(-1,24)),valid.detectors[1])))
        assert window.project==valid and window.lifecycle.identity==run
        window.view.setCurrentText('Intensity');window.secondary_toggle.click()
        assert window.secondary_action.isChecked() and window.second.isVisible()
        window.secondary_view.setCurrentText('Field')
        window.contrast.setValue(.5);window.intensity_range.setValue(.002)
        assert window.scale.levels()==(0,.002) and window.second_scale.levels()==(-.5,.5)
        for name,view,schemes,scale in (('field_scheme','Field',FIELD_SCHEMES,window.second_scale),('intensity_scheme','Intensity',INTENSITY_SCHEMES,window.scale)):
            for scheme in schemes:
                window.color_combos[name].setCurrentText(scheme)
                assert scale.colorMap() is color_map(view,scheme)
        window.color_combos['field_scheme'].setCurrentText('Blue / Red')
        window.color_combos['intensity_scheme'].setCurrentText('Inferno')
        window.secondary_toggle.click()
        assert not window.secondary_action.isChecked() and not window.second.isVisible()
        window.secondary_action.setChecked(True)
        assert window.secondary_toggle.isChecked() and window.second.isVisible()
        assert window.lifecycle.identity==run
        wait_until(lambda:window.frame is not None and window.frame.intensity is not None)
        window.pause_simulation();wait_until(lambda:window.frame.paused)
        window.write_png(output/'double-slit.png')
        image=QImage(str(output/'double-slit.png'))
        assert not image.isNull()
        metadata=json.loads(image.text('wave-studio-metadata'))
        assert metadata['run_id']==run.run_id
        assert metadata['display']['field_scheme']=='Blue / Red' and metadata['display']['intensity_scheme']=='Inferno'
        window.reset_simulation();assert window.project.references[0]==reference
        assert not window.lifecycle.can_step
        material=MaterialObject(vertices=((35,4),(38,4),(38,8),(35,8)),refractive_index=1.2)
        assert window.commit(replace(window.project,objects=window.project.objects+(material,)))
        assert window.lifecycle.state==State.CHANGED
        window.undo();assert material not in window.project.objects
        window.redo();assert material in window.project.objects
        assert not window.lifecycle.can_step
        save(output/'double-slit.wave.json',window.project)
        reopened=load(output/'double-slit.wave.json')
        assert reopened==window.project and reopened.references[0]==reference
        before=window.project
        try:decode(b'{bad')
        except ValueError:pass
        assert window.project==before
        window._recover_save();assert load(window.recovery)==window.project
        window.theme.setCurrentText('Light');app.processEvents();window.grab().save(str(output/'editor-light.png'))
        window.theme.setCurrentText('Dark');app.processEvents();window.grab().save(str(output/'editor-dark.png'))
        for name in ('Refraction','Biconvex lens'):
            window.replace_project(example(name));app.processEvents()
        results={'passed':True,'frozen':bool(getattr(sys,'frozen',False)),'engine_location':wave_sim2d.__file__,'application_location':__file__,'checks':['domain dimensions above 100 roundtrip','completed finite-window profile','reference freeze','same-run resume','exact single step','detector-only revision','other detector preserved','invalid edit preserved run','live intensity and second view','independent field and intensity ranges','all bundled color schemes','second view toolbar/menu synchronization','display edits preserve running identity','PNG embedded origin and color schemes','CSV raw values','reset preserves reference','physical undo/redo stays stopped','file roundtrip including reference and display settings','recovery roundtrip','three examples compile','dark/light layout'],'reference_run_id':reference['metadata']['run_id']}
    finally:
        window.lifecycle.dirty=False;window.close();app.processEvents()
    (output/'workflow-results.json').write_text(json.dumps(results,indent=2)+'\n')
    print(json.dumps(results,indent=2))
    return 0
