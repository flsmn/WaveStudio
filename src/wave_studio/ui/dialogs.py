from dataclasses import fields,replace
import json
import math
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (QDialog,QDialogButtonBox,QLineEdit,QPlainTextEdit,QComboBox,QLabel,QFormLayout,QVBoxLayout,QCheckBox,QScrollArea,QWidget,QApplication,QToolButton)
from wave_studio.domain.project import SourceObject,MaterialObject,WallObject,LensObject,DetectorObject
from .strings import COMPUTE_MODE_TOOLTIP,COMPUTE_MODE_TOOLTIPS
from .numbers import NumberBox,IntegerBox
from wave_studio.domain.resolution import pixel_dimensions,pixel_settings,resolution_preset,preset_name

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
        box=IntegerBox() if integer else NumberBox()
        box.setRange(1 if integer else -10000,2048 if integer else 10000)
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
        width,height=pixel_dimensions(project.settings)
        self.quality=QComboBox();self.quality.addItems(['Custom','Preview','Balanced','High Quality']);self.quality.setCurrentText(preset_name(width,height));form.addRow('Resolution preset',self.quality)
        from wave_studio.domain.quality import PRESET_AXIS_CELLS
        minimums=[]
        explanation='Width and height specify exact simulation cell counts. Editing a dimension selects Custom. Grid spacing and the time step are automatic.'
        for name,cells in PRESET_AXIS_CELLS.items():
            minimum=f'{name}: {cells:,} pixels on the longer axis; preserves aspect ratio, rounded to whole pixels.'
            minimums.append(minimum)
            self.quality.setItemData(self.quality.findText(name),minimum+'\n'+explanation,Qt.ItemDataRole.ToolTipRole)
        self.quality.setToolTip('\n'.join(minimums)+'\n'+explanation)
        self.advanced_settings=QWidget();advanced_form=QFormLayout(self.advanced_settings)
        advanced_form.setRowWrapPolicy(QFormLayout.RowWrapPolicy.WrapLongRows)
        from wave_studio.domain.resources import MAX_AXIS_CELLS
        for name,label,value in (('width','Width (pixels)',width),('height','Height (pixels)',height)):
            box=IntegerBox();box.setRange(8,MAX_AXIS_CELLS);box.setValue(value);box.setAccessibleName(label)
            box.setToolTip('Exact number of simulation cells on this axis.')
            self.boxes[name]=box;form.addRow(label,box)
        for name,label in [('border_width','Damped border width'),('border_rate','Border damping rate')]:
            box=NumberBox()
            box.setRange(0,100)
            box.setValue(getattr(project.settings,name));box.setKeyboardTracking(False);self.boxes[name]=box
            advanced_form.addRow(label,box)
        self.advanced_toggle=QToolButton();self.advanced_toggle.setText('Advanced settings')
        self.advanced_toggle.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self.advanced_toggle.setCheckable(True);self.advanced_toggle.setArrowType(Qt.ArrowType.RightArrow)
        self.advanced_toggle.toggled.connect(self._toggle_advanced)
        self.advanced_settings.hide();form.addRow(self.advanced_toggle);form.addRow(self.advanced_settings)
        self.device=QComboBox();self.device.addItems(['cpu','mps','auto']);self.device.setCurrentText(project.settings.device)
        import torch
        self.device.model().item(1).setEnabled(torch.backends.mps.is_available())
        advanced_form.addRow('Compute device',self.device)
        self.mode=QComboBox();self.mode.addItems(['Economical','Performance']);self.mode.setCurrentText(project.compute_mode);advanced_form.addRow('Compute mode',self.mode)
        self.mode.setToolTip(COMPUTE_MODE_TOOLTIP)
        for mode,tip in COMPUTE_MODE_TOOLTIPS.items():
            self.mode.setItemData(self.mode.findText(mode),tip,Qt.ItemDataRole.ToolTipRole)
        advanced_form.addRow(QLabel('Resource limits (saved with this project)'))
        from wave_studio.domain.resources import MAX_BUFFER_MIB,MAX_AXIS_CELLS
        for name,label,minimum,maximum in (('buffer_limit_mib','Numerical buffer budget (MiB)',1,MAX_BUFFER_MIB),('max_axis_cells','Maximum cells per axis',8,MAX_AXIS_CELLS)):
            box=IntegerBox();box.setRange(minimum,maximum);box.setSingleStep(64 if name=='buffer_limit_mib' else 256);box.setValue(getattr(project.settings,name));box.setKeyboardTracking(False)
            box.setToolTip('Admission limit, not a prediction of total memory or a guarantee that this computer can run the grid.')
            self.boxes[name]=box;advanced_form.addRow(label,box)
        body=QWidget();body.setLayout(form);scroll=QScrollArea();scroll.setWidgetResizable(True);scroll.setWidget(body);layout.addWidget(scroll)
        self.resize(600,min(420,QApplication.primaryScreen().availableGeometry().height()-80))
        note=QLabel('Width and height are simulation pixels. Entered dimensions are used exactly. Grid spacing and the time step are automatic; object coordinates stay in the existing project units.');note.setWordWrap(True);layout.addWidget(note)
        self.error=QLabel('');self.error.setWordWrap(True);layout.addWidget(self.error)
        buttons=QDialogButtonBox(QDialogButtonBox.StandardButton.Ok|QDialogButtonBox.StandardButton.Cancel);buttons.accepted.connect(self.apply);buttons.rejected.connect(self.reject);layout.addWidget(buttons)
        self.quality.currentTextChanged.connect(self.preset)
        for name,box in self.boxes.items():
            if name in ('width','height'):box.valueChanged.connect(self._custom_resolution)
            else:box.valueChanged.connect(self._refresh_estimate)
        self._refresh_estimate()

    def _toggle_advanced(self,expanded):
        self.advanced_settings.setVisible(expanded)
        self.advanced_toggle.setArrowType(Qt.ArrowType.DownArrow if expanded else Qt.ArrowType.RightArrow)
        self.resize(self.width(),min(720 if expanded else 420,self.screen().availableGeometry().height()-80))

    def _custom_resolution(self,*args):
        if not self._setting_preset:
            self.quality.setCurrentText('Custom');self._refresh_estimate()

    def _settings(self):
        settings=pixel_settings(self.project.settings,self.boxes['width'].value(),self.boxes['height'].value())
        return replace(settings,device=self.device.currentText(),**{k:b.value() for k,b in self.boxes.items() if k not in ('width','height')})

    def preset(self,name):
        if name!='Custom':
            width,height=resolution_preset(self.boxes['width'].value(),self.boxes['height'].value(),name)
            self._setting_preset=True
            try:self.boxes['width'].setValue(width);self.boxes['height'].setValue(height)
            finally:self._setting_preset=False
        self._refresh_estimate()

    def _refresh_estimate(self,*args):
        from wave_studio.domain.quality import estimate
        from wave_studio.domain.resources import summary
        try:
            settings=self._settings()
            result=estimate(replace(self.project,settings=settings),'Custom',settings.dx)
            self.error.setText(summary(settings,result.nx,result.ny)+f'\n{result.cells_per_wavelength:.1f} cells / shortest wavelength · predicted phase drift {result.phase_radians:.3f} rad over {result.path:.2f} reference lengths.')
        except (ValueError,ZeroDivisionError) as error:self.error.setText(str(error))

    def apply(self):
        try:
            settings=self._settings()
            candidate=replace(self.project,settings=settings,compute_mode=self.mode.currentText())
            self.validate(candidate);self.result_project=candidate;self.accept()
        except (ValueError,TypeError) as error:self.error.setText(str(error))
