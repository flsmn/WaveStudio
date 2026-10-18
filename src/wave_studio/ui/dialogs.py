from dataclasses import fields,replace
import json
import math
from PySide6.QtWidgets import (QDialog,QDialogButtonBox,QDoubleSpinBox,QSpinBox,QLineEdit,QPlainTextEdit,QComboBox,QLabel,QFormLayout,QVBoxLayout,QCheckBox,QScrollArea,QWidget,QApplication)
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
        form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        for f in fields(obj):
            if f.name=='id': continue
            value=getattr(obj,f.name)
            if value is None: continue
            if f.name in ('start','end'):
                for i,axis in enumerate(('x','y')):
                    box=self.number(value[i]); self.editors[(f.name,i)]=box; form.addRow(LABELS[f.name]+' '+axis,box)
            elif f.name=='vertices':
                editor=QPlainTextEdit(json.dumps(value)); editor.setMaximumHeight(110)
                editor.setTabChangesFocus(True)
                self.editors[f.name]=editor; form.addRow(LABELS[f.name],editor)
            elif isinstance(value,str):
                editor=QLineEdit(value); self.editors[f.name]=editor; form.addRow(LABELS.get(f.name,f.name),editor)
            else:
                editor=self.number(math.degrees(value) if f.name in ('phase','angle') else value,integer=f.name=='samples')
                label={'x':'Left x','y':'Bottom y'}.get(f.name,LABELS.get(f.name,f.name)) if isinstance(obj,WallObject) else LABELS.get(f.name,f.name)
                self.editors[f.name]=editor; form.addRow(label,editor)
        body=QWidget();body.setLayout(form);scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setWidget(body);layout.addWidget(scroll)
        self.resize(560, min(660,QApplication.primaryScreen().availableGeometry().height()-80))
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
                elif isinstance(editor,QPlainTextEdit):
                    raw=json.loads(editor.toPlainText())
                    if not isinstance(raw,list) or len(raw)<3 or any(not isinstance(p,(list,tuple)) or len(p)!=2 for p in raw):raise ValueError('Vertices must be a list of at least three [x, y] pairs.')
                    value=tuple(tuple(p) for p in raw)
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
        layout=QVBoxLayout(self);form=QFormLayout();form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows);self.boxes={};self._setting_preset=False
        self.quality=QComboBox();self.quality.addItems(['Custom','Preview','Balanced','High Quality']);self.quality.setCurrentText(project.settings.quality);form.addRow('Quality',self.quality)
        for name,label in [('width','Domain width'),('height','Domain height'),('dx','Grid spacing'),('courant','Time step / grid spacing'),('border_width','Damped border width'),('border_rate','Border damping rate')]:
            box=QDoubleSpinBox();box.setDecimals(12)
            box.setRange(.000001 if name in ('dx','courant') else 0,10000 if name in ('width','height') else 100)
            box.setValue(getattr(project.settings,name));box.setKeyboardTracking(False);self.boxes[name]=box;form.addRow(label,box)
        self.device=QComboBox();self.device.addItems(['cpu','mps','auto']);self.device.setCurrentText(project.settings.device)
        import torch
        self.device.model().item(1).setEnabled(torch.backends.mps.is_available())
        form.addRow('Compute device',self.device)
        self.mode=QComboBox();self.mode.addItems(['Economical','Performance']);self.mode.setCurrentText(project.compute_mode);form.addRow('Compute mode',self.mode)
        form.addRow(QLabel('Resource limits (saved with this project)'))
        from wave_studio.domain.resources import MAX_BUFFER_MIB,MAX_AXIS_CELLS
        for name,label,minimum,maximum in (('buffer_limit_mib','Numerical buffer budget (MiB)',1,MAX_BUFFER_MIB),('max_axis_cells','Maximum cells per axis',8,MAX_AXIS_CELLS)):
            box=QSpinBox();box.setRange(minimum,maximum);box.setSingleStep(64 if name=='buffer_limit_mib' else 256);box.setValue(getattr(project.settings,name));box.setKeyboardTracking(False)
            box.setToolTip('Admission limit, not a prediction of total memory or a guarantee that this computer can run the grid.')
            self.boxes[name]=box;form.addRow(label,box)
        body=QWidget();body.setLayout(form);scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setWidget(body);layout.addWidget(scroll)
        self.resize(600,min(720,QApplication.primaryScreen().availableGeometry().height()-80))
        note=QLabel('Geometry is preserved when quality changes. Preview may underresolve short waves and small structures. Final accuracy depends on the experiment.');note.setWordWrap(True);layout.addWidget(note)
        self.error=QLabel('');self.error.setWordWrap(True);layout.addWidget(self.error)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);buttons.accepted.connect(self.apply);buttons.rejected.connect(self.reject);layout.addWidget(buttons)
        self.quality.currentTextChanged.connect(self.preset)
        self.boxes['dx'].valueChanged.connect(self._custom_spacing)
        for name,box in self.boxes.items():
            if name!='dx':box.valueChanged.connect(lambda *args:self.preset(self.quality.currentText()))
        self.preset(self.quality.currentText())

    def _custom_spacing(self,*args):
        if not self._setting_preset:
            self.quality.setCurrentText('Custom');self.preset('Custom')

    def preset(self,name):
        from wave_studio.domain.quality import estimate
        from wave_studio.domain.resources import summary
        try:
            settings=replace(self.project.settings,**{k:b.value() for k,b in self.boxes.items()})
            result=estimate(replace(self.project,settings=settings),name,settings.dx if name=='Custom' else None)
            self._setting_preset=True
            self.boxes['dx'].setValue(result.dx)
            self._setting_preset=False
            self.error.setText(summary(settings,result.nx,result.ny)+f'\n{result.cells_per_wavelength:.1f} cells / shortest wavelength · predicted phase drift {result.phase_radians:.3f} rad over {result.path:.2f} reference lengths.')
        except (ValueError,ZeroDivisionError) as error:self.error.setText(str(error))

    def apply(self):
        try:
            settings=replace(self.project.settings,quality=self.quality.currentText(),device=self.device.currentText(),**{k:b.value() for k,b in self.boxes.items()})
            candidate=replace(self.project,settings=settings,compute_mode=self.mode.currentText())
            if self.quality.currentText()!='Custom':
                from wave_studio.domain.quality import estimate
                result=estimate(candidate,self.quality.currentText())
                if not result.supported:raise ValueError(result.reason)
                settings=replace(settings,dx=result.dx)
                candidate=replace(candidate,settings=settings)
            self.validate(candidate);self.result_project=candidate;self.accept()
        except (ValueError,TypeError) as error:self.error.setText(str(error))
