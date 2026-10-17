"""Scene editing, persistence, passive measurement and result export UI."""
from dataclasses import asdict,replace
from copy import deepcopy
import json
import math
import os
from pathlib import Path
from time import monotonic
from uuid import uuid4
import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt,QTimer,QRectF,QStandardPaths,QByteArray,QBuffer,QIODevice
from PySide6.QtGui import QAction,QKeySequence
from PySide6.QtWidgets import (QWidget,QVBoxLayout,QHBoxLayout,QLabel,QPushButton,QComboBox,QTreeWidget,QTreeWidgetItem,QDockWidget,QSplitter,QFileDialog,QMessageBox,QDialog)
from wave_sim2d import __version__ as engine_version
from wave_sim2d.geometry import lens_vertices
from wave_studio.domain.project import (Project,SourceObject,MaterialObject,WallObject,LensObject,DetectorObject)
from wave_studio.domain.history import History,change_kind
from wave_studio.simulation.compiler import compile_project,detector_spec
from wave_studio.simulation.lifecycle import Lifecycle,State
from wave_studio.simulation.worker import Frame,Failure
from wave_studio.persistence.projects import save,load,physical_data,atomic_write
from wave_studio.persistence.exports import export_csv
from .main_window import MainWindow as PrototypeWindow
from .dialogs import ObjectDialog,SettingsDialog


class MainWindow(PrototypeWindow):
    def __init__(self):
        self._image_configs={}
        self._empty_image=None
        self.history=History();self.selected=None;self.revisions={};self.profiles={}
        self.run_project=None;self.path=None;self.overlays=[];self._rebuilding=False
        self.polygon_points=None;self.measure_points=None;self._frames=0;self._last_rate=monotonic();self._last_steps=0
        super().__init__()
        self.recovery=Path(os.environ.get('WAVESTUDIO_RECOVERY_DIR',QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)))/'recovery.wave.json'
        self.recovery_timer=QTimer(self);self.recovery_timer.timeout.connect(self._recover_save);self.recovery_timer.start(30000)
        QTimer.singleShot(150,self._offer_recovery)
        QTimer.singleShot(0,lambda:self.resizeDocks([self.measure_dock],[240],Qt.Orientation.Vertical))
        self._rebuild_scene()

    def action(self,menu,title,callback,shortcut=None):
        action=QAction(title,self)
        if shortcut: action.setShortcut(shortcut)
        action.triggered.connect(callback);menu.addAction(action);return action

    def _build_ui(self):
        super()._build_ui()
        self.menuBar().clear()
        files=self.menuBar().addMenu('&File')
        self.action(files,'New experiment',self.new_project,QKeySequence.StandardKey.New)
        self.action(files,'Open…',self.open_project,QKeySequence.StandardKey.Open)
        self.action(files,'Save',self.save_project,QKeySequence.StandardKey.Save)
        self.action(files,'Save as…',lambda:self.save_project(True),QKeySequence.StandardKey.SaveAs)
        examples=files.addMenu('Examples')
        for name in ('Double slit','Refraction','Biconvex lens'):
            self.action(examples,name,lambda checked=False,n=name:self.open_example(n))
        files.addSeparator()
        self.action(files,'Export view as PNG…',self.export_png)
        self.action(files,'Export completed profile as CSV…',self.export_profile)
        self.action(files,'Export reference as CSV…',lambda:self.export_profile(True))
        files.addSeparator();self.action(files,'Quit',self.close,QKeySequence.StandardKey.Quit)
        edit=self.menuBar().addMenu('&Edit')
        self.undo_action=self.action(edit,'Undo',self.undo,QKeySequence.StandardKey.Undo)
        self.redo_action=self.action(edit,'Redo',self.redo,QKeySequence.StandardKey.Redo)
        add=edit.addMenu('Add')
        for name in ('Point source','Line source','Material rectangle','Polygon','Wall','Biconvex lens','Point detector','Detector line'):
            self.action(add,name,lambda checked=False,n=name:self.add_object(n))
        self.action(edit,'Edit properties…',self.edit_selected,'Ctrl+E')
        self.action(edit,'Duplicate',self.duplicate_selected,'Ctrl+D')
        self.action(edit,'Delete',self.delete_selected,'Backspace')
        self.action(edit,'Bring forward',lambda:self.reorder(1))
        self.action(edit,'Send backward',lambda:self.reorder(-1))
        self.action(edit,'Finish polygon',self.finish_polygon,'Return')
        view_menu=self.menuBar().addMenu('&View')
        self.secondary_action=QAction('Second view',self,checkable=True)
        self.secondary_action.toggled.connect(self._second_view);view_menu.addAction(self.secondary_action)
        self.action(view_menu,'Fit experiment',lambda:self.plot.setRange(xRange=(0,self.scene.grid.width),yRange=(0,self.scene.grid.height),padding=.02),'Ctrl+0')
        tools=self.menuBar().addMenu('&Tools')
        self.action(tools,'Simulation settings…',self.settings_dialog)
        self.action(tools,'Measure distance',lambda:self.start_measure('distance'))
        self.action(tools,'Measure angle',lambda:self.start_measure('angle'))
        help_menu=self.menuBar().addMenu('&Help');self.action(help_menu,'Quick guide',self.help)
        self.view.addItem('Intensity')
        panel=QWidget();side=QVBoxLayout(panel);side.setContentsMargins(12,12,12,12)
        row=QHBoxLayout();self.add_combo=QComboBox();self.add_combo.addItems(['Point source','Line source','Material rectangle','Polygon','Wall','Biconvex lens','Point detector','Detector line']);row.addWidget(self.add_combo)
        add_button=QPushButton('+');add_button.clicked.connect(lambda:self.add_object(self.add_combo.currentText()));row.addWidget(add_button);side.addLayout(row)
        self.tree=QTreeWidget();self.tree.setMinimumHeight(170);self.tree.setHeaderLabels(['Scene (top material last)']);self.tree.itemSelectionChanged.connect(self._selected);side.addWidget(self.tree,1)
        buttons=QHBoxLayout()
        for label,slot in [('Edit',self.edit_selected),('Copy',self.duplicate_selected),('Delete',self.delete_selected)]:
            b=QPushButton(label);b.clicked.connect(slot);buttons.addWidget(b)
        side.addLayout(buttons)
        self.properties=QLabel('Select an object to edit its properties.');self.properties.setWordWrap(True);side.addWidget(self.properties)
        self.edit_hint=QLabel('Pause to edit sources, materials and walls. Detectors remain editable while running.');self.edit_hint.setWordWrap(True);side.addWidget(self.edit_hint)
        self.warning=QLabel('');self.warning.setWordWrap(True);side.addWidget(self.warning)
        self.settings_button=QPushButton('Simulation settings…');self.settings_button.clicked.connect(self.settings_dialog);side.addWidget(self.settings_button)
        self.dock.setWidget(panel);self.dock.setMinimumWidth(290)
        self.inputs={}
        canvas=self.centralWidget().layout().itemAt(2).widget()
        canvas.layout().removeWidget(self.plot)
        self.splitter=QSplitter(Qt.Orientation.Horizontal)
        self.splitter.addWidget(self.plot)
        self.second=pg.PlotWidget();self.second.setAspectLocked(False);self.second.setLabel('bottom','x',units='reference length');self.second.setLabel('left','y',units='reference length');self.second.setXLink(self.plot);self.second.setYLink(self.plot);self.second.getViewBox().sigRangeChangedManually.connect(self._second_zoom)
        self.second_image=pg.ImageItem(axisOrder='row-major');self.second.addItem(self.second_image)
        self.second_scale=pg.ColorBarItem(values=(-1,1),colorMap=self._field_map(),interactive=False);self.second_scale.setImageItem(self.second_image,insert_in=self.second.getPlotItem())
        self.splitter.addWidget(self.second);self.second.hide();canvas.layout().insertWidget(1,self.splitter,1)
        self.secondary_view=QComboBox();self.secondary_view.addItems(['Intensity','Field','Material']);self.secondary_view.currentTextChanged.connect(self._views_changed);self.secondary_view.hide()
        self.centralWidget().layout().itemAt(1).layout().addWidget(self.secondary_view)
        self.plot.removeItem(self.source_marker)
        self.plot.scene().sigMouseClicked.connect(self.canvas_click)
        measure=QWidget();ml=QVBoxLayout(measure);bar=QHBoxLayout()
        self.detector_combo=QComboBox();self.detector_combo.currentIndexChanged.connect(self._plot_profiles);bar.addWidget(self.detector_combo)
        self.norm=QComboBox();self.norm.addItems(['Raw values','Shared maximum = 1']);self.norm.currentTextChanged.connect(self._plot_profiles);bar.addWidget(self.norm)
        freeze=QPushButton('Hold reference');freeze.clicked.connect(self.hold_reference);bar.addWidget(freeze)
        self.ref_combo=QComboBox();self.ref_combo.currentIndexChanged.connect(self._plot_profiles);bar.addWidget(self.ref_combo)
        self.profile_status=QLabel('No detector selected.');bar.addWidget(self.profile_status,1)
        ml.addLayout(bar);self.profile_plot=pg.PlotWidget();self.profile_plot.setLabel('left','Relative intensity');self.profile_plot.setLabel('bottom','Position',units='reference length');self.profile_plot.addLegend();ml.addWidget(self.profile_plot)
        self.measure_dock=QDockWidget('Measurements & references',self);self.measure_dock.setWidget(measure);self.measure_dock.setMinimumHeight(200);self.addDockWidget(Qt.DockWidgetArea.BottomDockWidgetArea,self.measure_dock)
        view_menu.addAction(self.dock.toggleViewAction());view_menu.addAction(self.measure_dock.toggleViewAction())
        self.mode_combo=QComboBox();self.mode_combo.addItems(['Economical','Performance']);self.mode_combo.currentTextChanged.connect(self._mode_changed);self.centralWidget().layout().itemAt(1).layout().addWidget(self.mode_combo)
        self.contrast.blockSignals(True);self.contrast.setDecimals(6);self.contrast.setRange(.000001,100);self.contrast.setValue(self.project.display.contrast);self.contrast.blockSignals(False)
        self.rate_label=QLabel('0 steps/s · 0 frames/s');self.centralWidget().layout().itemAt(3).layout().addWidget(self.rate_label)

    def _apply_theme(self,theme):
        super()._apply_theme(theme)
        if hasattr(self,'second'):
            color='#101925' if theme=='Dark' else '#eaf0f5'
            self.second.setBackground(color);self.profile_plot.setBackground(color)
            ink='#95a5b8' if theme=='Dark' else '#42566b'
            for chart in (self.second,self.profile_plot):
                for side in ('left','bottom','right'):chart.getAxis(side).setTextPen(pg.mkPen(ink));chart.getAxis(side).setPen(pg.mkPen(ink))
            for scale in (self.scale,self.second_scale):
                for side in ('left','right'):scale.getAxis(side).setTextPen(pg.mkPen(ink))

    def _refresh_controls(self):
        running=self.lifecycle.state==State.RUNNING
        self.run_button.setEnabled(not running);self.pause_button.setEnabled(running);self.step_button.setEnabled(self.lifecycle.can_step)
        self.state_label.setText(self.lifecycle.state.value)
        self.range_label.setText('Max' if self.project.display.view=='Intensity' else 'Range ±')
        self.settings_button.setEnabled(not running)
        self.undo_action.setEnabled(bool(self.history.undo_stack));self.redo_action.setEnabled(bool(self.history.redo_stack))
        self.setWindowTitle(('• ' if self.lifecycle.dirty else '')+'Wave Studio — '+self.project.name)
        for item,physical in self.overlays:
            if hasattr(item,'setMovable'): item.setMovable(not running or not physical)
            if hasattr(item,'movable'):item.movable=not running or not physical
            if hasattr(item,'translatable'): item.translatable=not running or not physical
            if hasattr(item,'getHandles'):
                for handle in item.getHandles(): handle.setEnabled(not running or not physical)

    def candidate_object(self,obj):
        collection='detectors' if isinstance(obj,DetectorObject) else 'objects'
        values=getattr(self.project,collection)
        return replace(self.project,**{collection:tuple(obj if old.id==obj.id else old for old in values)})

    def commit(self,candidate,history=True):
        if candidate==self.project:return True
        kind=change_kind(self.project,candidate)
        if kind=='physical' and self.lifecycle.state==State.RUNNING:
            self.message.setText('Pause before changing the physical setup.');self._rebuild_scene();return False
        try:
            if kind=='physical':scene=compile_project(candidate)
            else:
                candidate.validate()
                for detector in candidate.detectors:detector_spec(detector,0).validate(self.scene.grid)
                scene=self.scene
        except (ValueError,TypeError,OverflowError) as error:
            self.message.setText(str(error));self._rebuild_scene();return False
        before=self.project
        if history:self.history.push(before,candidate)
        self.project,self.scene=candidate,scene
        self.lifecycle.dirty=True
        if kind=='physical':
            self.lifecycle.physical_change();self.worker.submit('reset',self.lifecycle.identity);self.frame=None;self.profiles={};self.run_project=None
            self.message.setText('Setup changed. Press Run to start a fresh experiment.');self.time_label.setText('t = 0.000 · 0 steps')
        elif kind=='measurement':
            old={d.id:d for d in before.detectors}
            for d in candidate.detectors:
                if old.get(d.id)!=d:
                    self.revisions[d.id]=self.revisions.get(d.id,0)+1;self.profiles.pop(d.id,None)
            self.profiles={k:v for k,v in self.profiles.items() if any(d.id==k for d in candidate.detectors)}
            if self.lifecycle.run_id:self.worker.submit('detectors',self.lifecycle.identity,self.detector_specs())
        if before.compute_mode!=candidate.compute_mode:self.worker.submit('mode',self.lifecycle.identity,candidate.compute_mode)
        for widget,value in ((self.view,candidate.display.view),(self.theme,candidate.display.theme),(self.secondary_view,candidate.display.secondary_view),(self.mode_combo,candidate.compute_mode)):
            widget.blockSignals(True);widget.setCurrentText(value);widget.blockSignals(False)
        self.contrast.blockSignals(True);self.contrast.setValue(candidate.display.intensity_range if candidate.display.view=='Intensity' else candidate.display.contrast);self.contrast.blockSignals(False)
        self.secondary_action.blockSignals(True);self.secondary_action.setChecked(candidate.display.secondary_visible);self.secondary_action.blockSignals(False)
        self.second.setVisible(candidate.display.secondary_visible);self.secondary_view.setVisible(candidate.display.secondary_visible)
        if candidate.display.secondary_visible:self.splitter.setSizes([500,500])
        self._apply_theme(candidate.display.theme)
        if kind=='display':self._draw();self._plot_profiles()
        else:self._rebuild_scene()
        self._views_changed();self._refresh_controls();return True

    def detector_specs(self):return tuple(detector_spec(d,self.revisions.get(d.id,0)) for d in self.project.detectors)

    def _selected(self):
        items=self.tree.selectedItems();self.selected=items[0].data(0,Qt.ItemDataRole.UserRole) if items else None
        obj=self.find_selected()
        if obj:
            self.properties.setText(obj.name+'\n'+'\n'.join(f'{key}: {value}' for key,value in asdict(obj).items() if key not in ('id','vertices','name')))
        self._rebuild_overlays()

    def find_selected(self):return next((o for o in self.project.objects+self.project.detectors if o.id==self.selected),None)

    def _rebuild_scene(self):
        self._rebuilding=True;self.tree.blockSignals(True);self.tree.clear()
        for obj in self.project.objects+self.project.detectors:
            item=QTreeWidgetItem([obj.name]);item.setData(0,Qt.ItemDataRole.UserRole,obj.id);self.tree.addTopLevelItem(item)
            if obj.id==self.selected:item.setSelected(True)
        self.tree.blockSignals(False)
        current=self.detector_combo.currentData();self.detector_combo.blockSignals(True);self.detector_combo.clear()
        for d in self.project.detectors:self.detector_combo.addItem(d.name,d.id)
        index=self.detector_combo.findData(current)
        if index>=0:self.detector_combo.setCurrentIndex(index)
        self.detector_combo.blockSignals(False)
        self.ref_combo.blockSignals(True);self.ref_combo.clear();self.ref_combo.addItem('No reference',-1)
        for i,ref in enumerate(self.project.references):self.ref_combo.addItem(f'Reference {i+1}',i)
        if self.project.references:self.ref_combo.setCurrentIndex(len(self.project.references))
        self.ref_combo.blockSignals(False)
        self.scene_title.setText(self.project.name)
        self._update_grid_label();self._rebuilding=False;self._rebuild_overlays();self._draw();self._plot_profiles()

    def _rebuild_overlays(self):
        if self._rebuilding:return
        for item,_ in self.overlays:self.plot.removeItem(item)
        self.overlays=[]
        for obj in self.project.objects+self.project.detectors:
            color='#ffce7a' if obj.id==self.selected else '#a2aaba' if isinstance(obj,WallObject) else '#a5a0ef' if isinstance(obj,DetectorObject) else '#66d7bd'
            pen=pg.mkPen(color,width=2.5 if obj.id==self.selected else 1.3)
            if isinstance(obj,WallObject):
                roi=pg.RectROI((obj.x,obj.y),(obj.width,obj.height),pen=pen);roi.addScaleHandle((0,0),(1,1))
                get=lambda r=roi,o=obj:replace(o,x=float(r.pos().x()),y=float(r.pos().y()),width=float(r.size().x()),height=float(r.size().y()))
            elif isinstance(obj,(MaterialObject,LensObject)):
                vertices=obj.vertices if isinstance(obj,MaterialObject) else lens_vertices(obj.x,obj.y,obj.radius,obj.aperture,obj.angle)
                if isinstance(obj,LensObject):
                    outline=pg.PlotDataItem([p[0] for p in vertices+(vertices[0],)],[p[1] for p in vertices+(vertices[0],)],pen=pen);self.plot.addItem(outline);self.overlays.append((outline,True))
                    roi=pg.TargetItem(pos=(obj.x,obj.y),size=12,pen=pen,movable=True)
                    get=lambda r=roi,o=obj:replace(o,x=float(r.pos().x()),y=float(r.pos().y()))
                else:
                    roi=pg.PolyLineROI(vertices,closed=True,pen=pen)
                    get=lambda r=roi,o=obj:replace(o,vertices=self.roi_points(r))
            elif obj.end is not None:
                roi=pg.LineSegmentROI([obj.start,obj.end],pen=pen)
                get=lambda r=roi,o=obj:replace(o,start=self.roi_points(r)[0],end=self.roi_points(r)[1])
            else:
                roi=pg.TargetItem(pos=obj.start,size=12,pen=pen,movable=True)
                get=lambda r=roi,o=obj:replace(o,start=(float(r.pos().x()),float(r.pos().y())))
            if isinstance(roi,pg.PolyLineROI):
                for segment in roi.segments:
                    segment.sigClicked.disconnect(roi.segmentClicked)
                    segment.sigClicked.connect(lambda *args,i=obj.id:QTimer.singleShot(0,lambda:self.select_object(i)))
            elif hasattr(roi,'sigClicked'):
                roi.setAcceptedMouseButtons(Qt.MouseButton.LeftButton)
                roi.sigClicked.connect(lambda *args,i=obj.id:QTimer.singleShot(0,lambda:self.select_object(i)))
            self.plot.addItem(roi);self.overlays.append((roi,not isinstance(obj,DetectorObject)))
            signal=roi.sigPositionChangeFinished if isinstance(roi,pg.TargetItem) else roi.sigRegionChangeFinished
            signal.connect(lambda *args,g=get:self._drag_finished(g))
        self._refresh_controls()

    @staticmethod
    def roi_points(roi):
        return tuple((float(p.x()),float(p.y())) for p in [roi.mapToParent(pos) for _,pos in roi.getLocalHandlePositions()])

    def _drag_finished(self,getter):
        if not self._rebuilding:
            obj=getter()
            # Rebuild after the graphics event returns, avoiding deleted active handles.
            QTimer.singleShot(0,lambda:self.commit(self.candidate_object(obj)))

    def add_object(self,name):
        if name=='Polygon':
            if self.lifecycle.state==State.RUNNING:self.message.setText('Pause before drawing a material.');return
            self.polygon_points=[];self.message.setText('Click polygon vertices, then choose Edit → Finish polygon (Enter).');return
        obj={'Point source':lambda:SourceObject(start=(8,16)), 'Line source':lambda:SourceObject(name='Line source',start=(6,7),end=(6,25)), 'Material rectangle':lambda:MaterialObject(), 'Wall':lambda:WallObject(x=16,y=0,width=.5,height=12), 'Biconvex lens':LensObject, 'Point detector':lambda:DetectorObject(name='Point detector',start=(25,16),end=None,samples=1), 'Detector line':DetectorObject}[name]()
        if not isinstance(obj,DetectorObject) and self.lifecycle.state==State.RUNNING:self.message.setText('Pause before adding physical objects.');return
        dialog=ObjectDialog(obj,lambda o:compile_project(replace(self.project,**({'detectors':self.project.detectors+(o,)} if isinstance(o,DetectorObject) else {'objects':self.project.objects+(o,)}))),self)
        if dialog.exec()==QDialog.DialogCode.Accepted:
            obj=dialog.result_object;self.selected=obj.id
            self.commit(replace(self.project,**({'detectors':self.project.detectors+(obj,)} if isinstance(obj,DetectorObject) else {'objects':self.project.objects+(obj,)})))

    def edit_selected(self):
        obj=self.find_selected()
        if obj is None:return
        if not isinstance(obj,DetectorObject) and self.lifecycle.state==State.RUNNING:self.message.setText('Pause to edit the physical setup.');return
        dialog=ObjectDialog(obj,lambda o:compile_project(self.candidate_object(o)),self)
        if dialog.exec()==QDialog.DialogCode.Accepted:self.commit(self.candidate_object(dialog.result_object))

    def duplicate_selected(self):
        obj=self.find_selected()
        if obj is None:return
        copy=replace(obj,id=str(uuid4()),name=obj.name+' copy');self.selected=copy.id
        self.commit(replace(self.project,**({'detectors':self.project.detectors+(copy,)} if isinstance(obj,DetectorObject) else {'objects':self.project.objects+(copy,)})))

    def delete_selected(self):
        obj=self.find_selected()
        if obj:self.commit(replace(self.project,objects=tuple(o for o in self.project.objects if o.id!=obj.id),detectors=tuple(d for d in self.project.detectors if d.id!=obj.id)))

    def reorder(self,direction):
        objects=list(self.project.objects)
        i=next((i for i,o in enumerate(objects) if o.id==self.selected),-1)
        if i>=0 and 0<=i+direction<len(objects):objects[i],objects[i+direction]=objects[i+direction],objects[i];self.commit(replace(self.project,objects=tuple(objects)))

    def undo(self):
        if not self.history.undo_stack:return
        target=self.history.undo_stack[-1][0]
        target=replace(target,references=self.project.references)
        if self.lifecycle.state==State.RUNNING and change_kind(self.project,target)=='physical':self.message.setText('Pause before undoing a physical change.');return
        if self.commit(target,False):self.history.undo();self._refresh_controls()

    def redo(self):
        if not self.history.redo_stack:return
        target=replace(self.history.redo_stack[-1][1],references=self.project.references)
        if self.lifecycle.state==State.RUNNING and change_kind(self.project,target)=='physical':self.message.setText('Pause before redoing a physical change.');return
        if self.commit(target,False):self.history.redo();self._refresh_controls()

    def settings_dialog(self):
        if self.lifecycle.state==State.RUNNING:
            self.message.setText('Pause to change the grid or device. Compute mode can be changed from Tools.');return
        dialog=SettingsDialog(self.project,compile_project,self)
        if dialog.exec()==QDialog.DialogCode.Accepted:self.commit(dialog.result_project)

    def _draw(self):
        if not hasattr(self,'second'):return super()._draw()
        panes=[(self.project.display.view,self.image,self.scale,self.plot)]
        if self.second.isVisible():panes.append((self.secondary_view.currentText(),self.second_image,self.second_scale,self.second))
        for view,image,scale,plot in panes:
            if view=='Material':data=self.scene.refractive_index;levels=(1,max(2,float(data.max())));color=pg.ColorMap([0,1],['#162331','#6cdec8']);label='Refractive index'
            elif view=='Intensity':
                data=self.frame.intensity if self.frame is not None else None;levels=(0,self.project.display.intensity_range);color=pg.ColorMap([0,1],['#101925','#f0ca78']);label='Live mean field² (relative)'
            else:data=self.frame.field if self.frame is not None else None;levels=(-self.project.display.contrast,self.project.display.contrast);color=self._field_map();label='Field (relative)'
            if data is None:
                if self._empty_image is None or self._empty_image.shape!=self.scene.grid.shape:self._empty_image=np.zeros(self.scene.grid.shape,dtype=np.float32)
                data=self._empty_image
            g=self.scene.grid
            configuration=(view,levels,g.nx,g.ny,g.width,g.height)
            changed=self._image_configs.get(id(image))!=configuration
            if changed:
                scale.setColorMap(color);scale.setLevels(levels);scale.getAxis('left').setLabel(label);scale.axis.setWidth(75)
                self._image_configs[id(image)]=configuration
            if changed or image.image is not data:
                image.setImage(data,autoLevels=False)
                if changed:image.setRect(QRectF(0,0,g.width,g.height))

    def _view_changed(self,view):
        self.commit(replace(self.project,display=replace(self.project.display,view=view)))

    def _contrast_changed(self,value):
        if hasattr(self,'mode_combo'):self.commit(replace(self.project,display=replace(self.project.display,**{('intensity_range' if self.project.display.view=='Intensity' else 'contrast'):value})))

    def _theme_changed(self,theme):
        if hasattr(self,'mode_combo'):self.commit(replace(self.project,display=replace(self.project.display,theme=theme)))

    def _mode_changed(self,mode):
        self.commit(replace(self.project,compute_mode=mode))

    def _views_changed(self,*args):
        if args and isinstance(args[0],str) and self.project.display.secondary_view!=self.secondary_view.currentText():
            self.commit(replace(self.project,display=replace(self.project.display,secondary_view=self.secondary_view.currentText())));return
        if self.lifecycle.run_id:self.worker.submit('views',self.lifecycle.identity,(self.project.display.view, self.secondary_view.currentText() if self.second.isVisible() else self.project.display.view))
        self._draw()

    def _second_zoom(self,*args):
        ranges=self.second.viewRange();self.plot.setRange(xRange=ranges[0],yRange=ranges[1],padding=0)

    def _second_view(self,visible):
        self.commit(replace(self.project,display=replace(self.project.display,secondary_visible=visible)))

    def run_simulation(self):
        try:
            scene=compile_project(self.project);fresh=self.lifecycle.run();self.scene=scene
            if fresh:self.run_project=self.project;self.profiles={};self.frame=None;self._last_steps=0;self._last_rate=monotonic();self._frames=0
            self.worker.submit('start' if fresh else 'resume',self.lifecycle.identity,(scene,self.detector_specs()),self.project.settings.device)
            self.worker.submit('mode',self.lifecycle.identity,self.project.compute_mode);self._views_changed()
            self.message.setText('Experiment running. Intensity view is a live preview; detector windows provide completed measurements.')
        except Exception as error:self.lifecycle.fail(str(error));self.message.setText(str(error))
        self._refresh_controls()

    def reset_simulation(self):
        super().reset_simulation();self.profiles={};self.run_project=None;self._plot_profiles()

    def _poll(self):
        result=self.worker.latest.take()
        if result is None or not self.lifecycle.accepts(result.identity):return
        if isinstance(result,Failure):
            self.lifecycle.fail(result.message);self.frame=None;self.profiles={};self.message.setText(result.message);self._draw();self._plot_profiles();self._refresh_controls();return
        self.frame=result;self._frames+=1
        for key,profile in (result.profiles or {}).items():
            if profile['measurement_revision']==self.revisions.get(key,0):
                self.profiles[key]={**profile,'metadata':self.metadata()}
        self.time_label.setText(f't = {result.time:.3f} · {result.steps:,} steps')
        self._draw();self._plot_profiles()
        now=monotonic()
        if now-self._last_rate>=1:
            self.rate_label.setText(f'{(result.steps-self._last_steps)/(now-self._last_rate):.0f} steps/s · {self._frames/(now-self._last_rate):.0f} frames/s')
            self._last_rate=now;self._last_steps=result.steps;self._frames=0

    def metadata(self):
        return {'scene':physical_data(self.run_project or self.project),'scene_revision':self.lifecycle.scene_revision,'run_id':self.lifecycle.run_id,'generation':self.lifecycle.generation,'engine_version':engine_version,'grid':asdict(self.scene.grid),'dt':self.scene.grid.dt,'backend':self.frame.backend if self.frame else self.project.settings.device,'dtype':'float32','time':self.frame.time if self.frame else 0,'steps':self.frame.steps if self.frame else 0}

    def _plot_profiles(self,*args):
        if not hasattr(self,'profile_plot'):return
        self.profile_plot.clear()
        current=self.profiles.get(self.detector_combo.currentData())
        index=self.ref_combo.currentData();reference=self.project.references[index] if isinstance(index,int) and 0<=index<len(self.project.references) else None
        series=[('Current',current,'#65d5bd' if self.project.display.theme=='Dark' else '#147964'),('Reference',reference,'#f2bd72' if self.project.display.theme=='Dark' else '#925700')]
        origin=current or reference
        axis=0
        if origin:
            points=np.array(origin['positions']);axis=1 if np.ptp(points[:,1])>np.ptp(points[:,0]) else 0
            self.profile_plot.setLabel('bottom','y' if axis==1 else 'x',units='reference length')
        denominator=max([max(p['values'],default=0) for _,p,_ in series if p]+[1e-30]) if self.norm.currentText()!='Raw values' else 1
        for name,profile,color in series:
            if profile:
                positions=np.array(profile['positions'])
                self.profile_plot.plot(positions[:,axis],np.array(profile['values'])/denominator,pen=pg.mkPen(color,width=2),symbol='o' if len(positions)==1 else None,name=name)
                self.profile_plot.setLabel('bottom','y' if axis==1 else 'x',units='reference length')
        if current:self.profile_status.setText(f"{current['status'].capitalize()} · {current['elapsed']:.2f}/{current['duration']:g} time · {current['sample_count']} samples")
        else:self.profile_status.setText('Waiting for detector data.' if self.project.detectors else 'Add a passive detector to measure intensity.')
        if current and reference and current['positions']!=reference['positions']:
            self.profile_status.setText(self.profile_status.text()+' · Different sampling paths; compare coordinates.')

    def hold_reference(self):
        profile=self.profiles.get(self.detector_combo.currentData())
        if not profile or profile['status']!='complete':self.message.setText('Wait for a completed detector window before holding a reference.');return
        self.project=replace(self.project,references=(self.project.references+(deepcopy(profile),))[-4:]);self.lifecycle.dirty=True;self._rebuild_scene();self._refresh_controls()

    def export_profile(self,reference=False):
        index=self.ref_combo.currentData()
        profile=self.project.references[index] if reference and isinstance(index,int) and 0<=index<len(self.project.references) else None if reference else self.profiles.get(self.detector_combo.currentData())
        if not profile or profile['status']!='complete':self.message.setText('Select a completed profile or a saved reference.');return
        path,_=QFileDialog.getSaveFileName(self,'Export relative intensity','profile.csv','CSV (*.csv)')
        if path:
            try:export_csv(path,deepcopy(profile));self.message.setText('Profile exported.')
            except (OSError,ValueError) as error:self.message.setText(str(error))

    def write_png(self,path):
        image=self.plot.grab().toImage();image.setText('wave-studio-metadata',json.dumps({**self.metadata(),'view':self.project.display.view,'display':asdict(self.project.display),'status':'live preview' if self.project.display.view=='Intensity' else 'snapshot'},allow_nan=False))
        data=QByteArray();buffer=QBuffer(data);buffer.open(QIODevice.OpenModeFlag.WriteOnly)
        if not image.save(buffer,'PNG'):raise OSError('Could not encode PNG.')
        atomic_write(path,bytes(data))

    def export_png(self):
        path,_=QFileDialog.getSaveFileName(self,'Export view','experiment.png','PNG (*.png)')
        if path:
            try:self.write_png(path);self.message.setText('View exported with experiment metadata.')
            except (OSError,ValueError) as error:self.message.setText(str(error))

    def confirm_discard(self):
        if not self.lifecycle.dirty:return True
        choice=QMessageBox.question(self,'Unsaved experiment','Save changes to this experiment?',QMessageBox.StandardButton.Save|QMessageBox.StandardButton.Discard|QMessageBox.StandardButton.Cancel)
        if choice==QMessageBox.StandardButton.Save:return self.save_project()
        return choice==QMessageBox.StandardButton.Discard

    def replace_project(self,project,path=None):
        scene=compile_project(project)
        self.lifecycle.reset();self.worker.submit('reset',self.lifecycle.identity)
        self.project,self.scene,self.path=project,scene,path;self.lifecycle=Lifecycle(project.id);self.frame=None;self.profiles={};self.run_project=None;self.history=History();self.revisions={};self.selected=None
        for widget,value in ((self.view,project.display.view),(self.theme,project.display.theme),(self.secondary_view,project.display.secondary_view),(self.mode_combo,project.compute_mode)):
            widget.blockSignals(True);widget.setCurrentText(value);widget.blockSignals(False)
        self.contrast.blockSignals(True);self.contrast.setValue(project.display.intensity_range if project.display.view=='Intensity' else project.display.contrast);self.contrast.blockSignals(False)
        self.secondary_action.blockSignals(True);self.secondary_action.setChecked(project.display.secondary_visible);self.secondary_action.blockSignals(False)
        self.second.setVisible(project.display.secondary_visible);self.secondary_view.setVisible(project.display.secondary_visible)
        if project.display.secondary_visible:self.splitter.setSizes([500,500])
        self._apply_theme(project.display.theme);self.lifecycle.dirty=False
        self._rebuild_scene();self._refresh_controls();self.message.setText('Experiment ready. Press Run to start.');self.time_label.setText('t = 0.000 · 0 steps')
        self.plot.setRange(xRange=(0,scene.grid.width),yRange=(0,scene.grid.height),padding=.02)

    def new_project(self):
        if self.confirm_discard():self.replace_project(Project(name='Untitled experiment',objects=()))

    def open_project(self):
        path,_=QFileDialog.getOpenFileName(self,'Open experiment','','Wave Studio (*.wave.json *.json)')
        if not path:return
        try:project=load(path)
        except (OSError,ValueError) as error:self.message.setText(str(error));return
        if self.confirm_discard():self.replace_project(project,Path(path))

    def save_project(self,save_as=False):
        path=self.path
        if save_as or path is None:
            value,_=QFileDialog.getSaveFileName(self,'Save experiment','experiment.wave.json','Wave Studio (*.wave.json)')
            if not value:return False
            path=Path(value)
        try:save(path,self.project)
        except (OSError,ValueError) as error:self.message.setText(str(error));return False
        self.path=path;self.lifecycle.dirty=False;self._refresh_controls();self.message.setText('Experiment saved.');return True

    def open_example(self,name):
        from wave_studio.examples import example
        if self.confirm_discard():self.replace_project(example(name))

    def _recover_save(self):
        if not self.lifecycle.dirty:return
        try:self.recovery.parent.mkdir(parents=True,exist_ok=True);save(self.recovery,self.project)
        except (OSError,ValueError) as error:self.message.setText('Recovery could not be saved: '+str(error))

    def _offer_recovery(self):
        if self.recovery.exists():
            try:project=load(self.recovery)
            except (OSError,ValueError):return
            if QMessageBox.question(self,'Recover experiment','Restore the last automatically saved experiment?',QMessageBox.StandardButton.Yes|QMessageBox.StandardButton.No)==QMessageBox.StandardButton.Yes:
                self.replace_project(project);self.lifecycle.dirty=True;self._refresh_controls()

    def select_object(self,identifier):
        for index in range(self.tree.topLevelItemCount()):
            item=self.tree.topLevelItem(index)
            if item.data(0,Qt.ItemDataRole.UserRole)==identifier:self.tree.setCurrentItem(item);return

    def canvas_click(self,event):
        if not (self.polygon_points is not None or self.measure_points is not None):
            point=self.plot.getViewBox().mapSceneToView(event.scenePos())
            tolerance=(self.plot.viewRange()[0][1]-self.plot.viewRange()[0][0])*12/max(1,self.plot.width())
            nearest=min(((math.dist((point.x(),point.y()),o.start if hasattr(o,'start') else (o.x,o.y)),o.id) for o in self.project.objects+self.project.detectors if isinstance(o,(SourceObject,DetectorObject,LensObject))),default=(float('inf'),None))
            if nearest[0]<tolerance:QTimer.singleShot(0,lambda:self.select_object(nearest[1]))
            return
        if event.button()!=Qt.MouseButton.LeftButton:return
        point=self.plot.getViewBox().mapSceneToView(event.scenePos());p=(float(point.x()),float(point.y()))
        if self.polygon_points is not None:
            self.polygon_points.append(p);self.message.setText(f'{len(self.polygon_points)} vertices. Press Enter to finish.');return
        kind,points=self.measure_points;points.append(p)
        if len(points)==(2 if kind=='distance' else 3):
            if kind=='distance':text=f'Distance: {math.dist(*points):.5f} reference lengths'
            else:
                a=np.array(points[0])-points[1];b=np.array(points[2])-points[1];den=np.linalg.norm(a)*np.linalg.norm(b)
                text=f'Angle: {math.degrees(math.acos(float(np.clip(np.dot(a,b)/den,-1,1)))):.3f}°' if den else 'Choose distinct points for an angle.'
            self.message.setText(text);line=pg.PlotDataItem([p[0] for p in points],[p[1] for p in points],pen=pg.mkPen('#f3cd7e',width=2),symbol='o');self.plot.addItem(line);self.overlays.append((line,False));self.measure_points=None

    def finish_polygon(self):
        if self.polygon_points is None:return
        obj=MaterialObject(name='Polygon',vertices=tuple(self.polygon_points))
        if self.commit(replace(self.project,objects=self.project.objects+(obj,))):self.polygon_points=None

    def start_measure(self,kind):self.measure_points=(kind,[]);self.polygon_points=None;self.message.setText('Click two endpoints.' if kind=='distance' else 'Click first point, vertex, then second point.')

    def help(self):
        QMessageBox.information(self,'Wave Studio guide','Add sources, materials, walls and passive detectors from Edit → Add. Drag objects or use Edit properties for exact coordinates. Materials later in the list override earlier materials.\n\nRun starts the experiment. Pause before physical edits; only Run starts the changed setup. Step advances a paused run once. Reset clears current results and preserves references.\n\nIntensity is a live preview of relative field squared. Detector measurements settle, accumulate over a finite window, then become complete. Choose windows long enough for propagation and beating between source frequencies. Hold a completed profile as a reference; up to four are saved with the experiment. CSV always exports raw completed values.\n\nGeometry uses fixed reference lengths. The scalar 2D model has no polarization, absolute optical power or precision 3D lens prediction. Boundaries use a damped border. Quality and compute mode are independent.\n\nRecovery: one file, at most 8 MiB, every 30 seconds while modified. Project files contain setup and references, never a resumable wave field.')

    def closeEvent(self,event):
        if not self.confirm_discard():event.ignore();return
        super().closeEvent(event)
        if event.isAccepted():
            self.recovery_timer.stop()
            if self.recovery.exists():
                try:self.recovery.unlink()
                except OSError:pass
