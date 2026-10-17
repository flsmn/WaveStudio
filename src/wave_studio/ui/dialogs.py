from dataclasses import fields,replace
import json
import math
from PySide6.QtWidgets import (QDialog,QDialogButtonBox,QDoubleSpinBox,QSpinBox,QLineEdit,QPlainTextEdit,QComboBox,QLabel,QFormLayout,QVBoxLayout,QCheckBox)
from wave_studio.domain.project import SourceObject,MaterialObject,WallObject,LensObject,DetectorObject

LABELS={'start':'Start','end':'End','x':'Centre x','y':'Centre y','width':'Width','height':'Height','radius':'Curvature radius','aperture':'Aperture','refractive_index':'Refractive index','damping_rate':'Damping / time','wavelength':'Reference wavelength','amplitude':'Forcing amplitude','phase':'Phase (degrees)','angle':'Rotation (degrees)','samples':'Spatial samples','settling':'Settling time','window':'Window duration','vertices':'Vertices: [[x, y], …]','name':'Name'}


class ObjectDialog(QDialog):
    def __init__(self,obj,validate,parent=None):
        super().__init__(parent)
        self.setWindowTitle('Edit '+obj.name)
        self.obj,self.validate,self.result_object=obj,validate,None
        self.editors={}
        layout=QVBoxLayout(self)
        form=QFormLayout()
        for f in fields(obj):
            if f.name=='id': continue
            value=getattr(obj,f.name)
            if value is None: continue
            if f.name in ('start','end'):
                for i,axis in enumerate(('x','y')):
                    box=self.number(value[i]); self.editors[(f.name,i)]=box; form.addRow(LABELS[f.name]+' '+axis,box)
            elif f.name=='vertices':
                editor=QPlainTextEdit(json.dumps(value)); editor.setMaximumHeight(110)
                self.editors[f.name]=editor; form.addRow(LABELS[f.name],editor)
            elif isinstance(value,str):
                editor=QLineEdit(value); self.editors[f.name]=editor; form.addRow(LABELS.get(f.name,f.name),editor)
            else:
                editor=self.number(math.degrees(value) if f.name in ('phase','angle') else value,integer=f.name=='samples')
                self.editors[f.name]=editor; form.addRow(LABELS.get(f.name,f.name),editor)
        layout.addLayout(form)
        self.error=QLabel(''); self.error.setWordWrap(True); self.error.setStyleSheet('color:#dd805f');layout.addWidget(self.error)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel)
        buttons.accepted.connect(self.apply);buttons.rejected.connect(self.reject);layout.addWidget(buttons)

    def number(self,value,integer=False):
        box=QSpinBox() if integer else QDoubleSpinBox()
        box.setRange(1 if integer else -10000,2048 if integer else 10000)
        if not integer: box.setDecimals(5);box.setSingleStep(.25)
        box.setValue(value)
        return box

    def apply(self):
        try:
            changes={}
            for key,editor in self.editors.items():
                if isinstance(key,tuple): continue
                if isinstance(editor,QLineEdit): value=editor.text()
                elif isinstance(editor,QPlainTextEdit): value=tuple(tuple(p) for p in json.loads(editor.toPlainText()))
                else: value=editor.value()
                changes[key]=math.radians(value) if key in ('phase','angle') else value
            for key in ('start','end'):
                if (key,0) in self.editors: changes[key]=tuple(self.editors[(key,i)].value() for i in (0,1))
            candidate=replace(self.obj,**changes)
            self.validate(candidate)
            self.result_object=candidate
            self.accept()
        except (ValueError,TypeError,OverflowError) as error: self.error.setText(str(error))


class SettingsDialog(QDialog):
    def __init__(self,project,validate,parent=None):
        super().__init__(parent)
        self.setWindowTitle('Simulation settings')
        self.project,self.validate,self.result_project=project,validate,None
        layout=QVBoxLayout(self);form=QFormLayout();self.boxes={}
        self.quality=QComboBox();self.quality.addItems(['Custom','Preview','Balanced','High Quality']);form.addRow('Quality',self.quality)
        for name,label in [('width','Domain width'),('height','Domain height'),('dx','Grid spacing'),('courant','Time step / grid spacing'),('border_width','Damped border width'),('border_rate','Border damping rate')]:
            box=QDoubleSpinBox();box.setDecimals(6);box.setRange(.000001 if name in ('dx','courant') else 0,100);box.setValue(getattr(project.settings,name));self.boxes[name]=box;form.addRow(label,box)
        self.device=QComboBox();self.device.addItems(['cpu','mps','auto']);self.device.setCurrentText(project.settings.device)
        import torch
        self.device.model().item(1).setEnabled(torch.backends.mps.is_available())
        form.addRow('Compute device',self.device)
        self.mode=QComboBox();self.mode.addItems(['Economical','Performance']);self.mode.setCurrentText(project.compute_mode);form.addRow('Compute mode',self.mode)
        self.quality.currentTextChanged.connect(self.preset)
        layout.addLayout(form)
        note=QLabel('Geometry is preserved when quality changes. Preview may underresolve short waves and small structures. Final accuracy depends on the experiment.');note.setWordWrap(True);layout.addWidget(note)
        self.error=QLabel('');self.error.setWordWrap(True);layout.addWidget(self.error)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);buttons.accepted.connect(self.apply);buttons.rejected.connect(self.reject);layout.addWidget(buttons)

    def preset(self,name):
        if name=='Custom': return
        sources=[o for o in self.project.objects if isinstance(o,SourceObject)]
        materials=[o for o in self.project.objects if isinstance(o,(MaterialObject,LensObject))]
        wavelength=min((o.wavelength for o in sources),default=2)
        n=max((o.refractive_index for o in materials),default=1)
        target=wavelength/n/{'Preview':8,'Balanced':12,'High Quality':20}[name]
        walls=[o for o in self.project.objects if isinstance(o,WallObject)]
        target=min([target]+[min(o.width,o.height)/2 for o in walls])
        # Power-of-two subdivision of project units preserves the fixed 32×32 domain.
        dx=2**math.floor(math.log2(target))
        self.boxes['dx'].setValue(dx)
        self.boxes['courant'].setValue(.5)

    def apply(self):
        try:
            settings=replace(self.project.settings,device=self.device.currentText(),**{k:b.value() for k,b in self.boxes.items()})
            candidate=replace(self.project,settings=settings,compute_mode=self.mode.currentText())
            self.validate(candidate);self.result_project=candidate;self.accept()
        except (ValueError,TypeError) as error:self.error.setText(str(error))
