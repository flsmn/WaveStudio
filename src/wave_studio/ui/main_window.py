from dataclasses import replace
import math
import numpy as np
import pyqtgraph as pg
from PySide6.QtCore import Qt, QTimer, QRectF
from PySide6.QtGui import QAction, QColor, QPalette, QKeySequence
from PySide6.QtWidgets import (
    QApplication, QComboBox, QDockWidget, QDoubleSpinBox, QFormLayout,
    QFrame, QHBoxLayout, QLabel, QMainWindow, QMessageBox, QPushButton,
    QSplitter, QTreeWidget, QTreeWidgetItem, QVBoxLayout, QWidget,
)
from wave_studio.domain.project import Project, SourceObject, with_source
from wave_studio.simulation.compiler import compile_project
from wave_studio.simulation.lifecycle import Lifecycle, State
from wave_studio.simulation.worker import SimulationWorker, Frame, Failure
from . import strings
from .flow_layout import FlowLayout


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.project = Project()
        self.lifecycle = Lifecycle(self.project.id)
        self.scene = compile_project(self.project)
        self.frame = None
        self._syncing = False
        self.setWindowTitle(strings.TITLE + ' — ' + self.project.name)
        self.resize(1320,860)
        self.setMinimumSize(980,660)
        self.worker = SimulationWorker(self)
        self.worker.start()
        self._build_ui()
        self._apply_theme('Dark')
        self._refresh_controls()
        self._draw()
        self.timer = QTimer(self)
        self.timer.timeout.connect(self._poll)
        self.timer.start(33)

    def _build_ui(self):
        file_menu = self.menuBar().addMenu('&File')
        quit_action = QAction('Quit',self,shortcut=QKeySequence.StandardKey.Quit)
        quit_action.triggered.connect(self.close)
        file_menu.addAction(quit_action)
        view_menu = self.menuBar().addMenu('&View')
        root = QWidget()
        layout = QVBoxLayout(root)
        layout.setContentsMargins(22,12,22,14)
        layout.setSpacing(14)
        header = QHBoxLayout()
        heading = QLabel('Wave Studio')
        self.heading=heading
        heading.setStyleSheet('font-size:24px;font-weight:650;')
        header.addWidget(heading)
        subtitle = QLabel(strings.SUBTITLE)
        subtitle.setObjectName('muted')
        subtitle.setWordWrap(True)
        subtitle.setMinimumWidth(0)
        header.addWidget(subtitle)
        header.addStretch()
        self.theme = QComboBox()
        self.theme.addItems(['Dark','Light'])
        self.theme.setAccessibleName('Color theme')
        self.theme.currentTextChanged.connect(self._theme_changed)
        header.addWidget(self.theme)
        layout.addLayout(header)
        controls = FlowLayout()
        self.run_button = QPushButton('▶  Run')
        self.run_button.setObjectName('primary')
        self.run_button.setShortcut('Ctrl+R')
        self.pause_button = QPushButton('Ⅱ  Pause')
        self.step_button = QPushButton('Step')
        self.reset_button = QPushButton('Reset')
        for button,slot in ((self.run_button,self.run_simulation),(self.pause_button,self.pause_simulation),(self.step_button,self.step_simulation),(self.reset_button,self.reset_simulation)):
            button.setMinimumHeight(36)
            button.clicked.connect(slot)
            controls.addWidget(button)
        controls.addStretch()
        controls.addWidget(QLabel('View'))
        self.view = QComboBox()
        self.view.addItems(['Field','Material'])
        self.view.currentTextChanged.connect(self._view_changed)
        controls.addWidget(self.view)
        self.range_label=QLabel('Range ±');controls.addWidget(self.range_label)
        self.contrast = QDoubleSpinBox()
        self.contrast.setRange(.01,100)
        self.contrast.setValue(1)
        self.contrast.setSingleStep(.1)
        self.contrast.setAccessibleName('Field color range')
        self.contrast.valueChanged.connect(self._contrast_changed)
        controls.addWidget(self.contrast)
        layout.addLayout(controls)
        self.plot = pg.PlotWidget()
        self.plot.setAspectLocked(True)
        self.plot.setLabel('bottom','x',units='reference length')
        self.plot.setLabel('left','y',units='reference length')
        self.plot.showGrid(x=True,y=True,alpha=.12)
        self.plot.setMouseEnabled(x=True,y=True)
        self.plot.setMenuEnabled(False)
        self.image = pg.ImageItem(axisOrder='row-major',autoDownsample=True)
        self.plot.addItem(self.image)
        self.source_marker = pg.ScatterPlotItem(size=10,pen=pg.mkPen('#ffffff',width=1.5),brush=pg.mkBrush('#55dbc0'))
        self.plot.addItem(self.source_marker)
        self.source_marker.setData([16],[16])
        self.scale = pg.ColorBarItem(values=(-1,1),colorMap=self._field_map(),interactive=False)
        self.scale.setImageItem(self.image,insert_in=self.plot.getPlotItem())
        canvas = QWidget()
        canvas_layout = QVBoxLayout(canvas)
        canvas_layout.setContentsMargins(0,0,0,0)
        caption = QHBoxLayout()
        self.scene_title = QLabel(self.project.name)
        self.scene_title.setStyleSheet('font-size:15px;font-weight:600;')
        caption.addWidget(self.scene_title)
        caption.addStretch()
        self.grid_label = QLabel('')
        self.grid_label.setObjectName('muted')
        caption.addWidget(self.grid_label)
        canvas_layout.addLayout(caption)
        canvas_layout.addWidget(self.plot,1)
        self.message = QLabel(strings.READY)
        self.message.setWordWrap(True)
        canvas_layout.addWidget(self.message)
        layout.addWidget(canvas,1)
        footer = FlowLayout()
        self.state_label = QLabel('Ready')
        self.time_label = QLabel('t = 0.000  ·  0 steps')
        footer.addWidget(self.state_label)
        footer.addStretch()
        footer.addWidget(self.time_label)
        layout.addLayout(footer)
        self.setCentralWidget(root)
        scene_panel = QWidget()
        side = QVBoxLayout(scene_panel)
        side.setContentsMargins(14,14,14,14)
        side.setSpacing(14)
        self.tree = QTreeWidget()
        self.tree.setHeaderLabels(['Experiment'])
        self.tree.addTopLevelItem(QTreeWidgetItem(['Point source']))
        self.tree.setMaximumHeight(150)
        side.addWidget(self.tree)
        label = QLabel('Source properties')
        label.setStyleSheet('font-weight:600;')
        side.addWidget(label)
        form = QFormLayout()
        self.inputs = {}
        source = self.project.objects[0]
        for name,title,value,low,high in (
            ('x','Position x',source.start[0],3.125,28.875),
            ('y','Position y',source.start[1],3.125,28.875),
            ('wavelength','Wavelength',source.wavelength,.25,16),
            ('amplitude','Amplitude',source.amplitude,0,20),
            ('phase','Phase (°)',0,-3600,3600),
        ):
            box = QDoubleSpinBox()
            box.setDecimals(3)
            box.setRange(low,high)
            box.setValue(value)
            box.setSingleStep(.125 if name in ('x','y') else .1)
            box.setKeyboardTracking(False)
            box.setAccessibleName(title)
            box.editingFinished.connect(self._edit_source)
            form.addRow(title,box)
            self.inputs[name] = box
        side.addLayout(form)
        self.edit_hint = QLabel(strings.PAUSE_TO_EDIT)
        self.edit_hint.setWordWrap(True)
        self.edit_hint.setObjectName('muted')
        side.addWidget(self.edit_hint)
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        side.addWidget(line)
        side.addWidget(QLabel('Compute device'))
        self.device = QComboBox()
        self.device.addItems(['CPU','MPS'])
        # MPS is only offered when a device is actually available.
        import torch
        self.device.model().item(1).setEnabled(torch.backends.mps.is_available())
        self.device.currentTextChanged.connect(self._device_changed)
        side.addWidget(self.device)
        self.warning = QLabel('')
        self.warning.setWordWrap(True)
        self.warning.setObjectName('muted')
        side.addWidget(self.warning)
        side.addStretch()
        self.dock = QDockWidget('Scene & properties',self)
        self.dock.setWidget(scene_panel)
        self.dock.setMinimumWidth(255)
        self.dock.setFeatures(QDockWidget.DockWidgetFeature.DockWidgetMovable)
        self.addDockWidget(Qt.DockWidgetArea.LeftDockWidgetArea,self.dock)
        view_menu.addAction(self.dock.toggleViewAction())
        self._update_grid_label()

    @staticmethod
    def _field_map():
        return pg.ColorMap([0,.5,1],['#3684d6','#101925','#f0bd74'])

    def _apply_theme(self,theme):
        dark = theme == 'Dark'
        bg, panel, text, muted, border = ('#10151c','#181f29','#e6edf5','#95a5b8','#2b3544') if dark else ('#f4f6f8','#ffffff','#172536','#546579','#d6dfe8')
        factor=self.project.display.text_scale
        self.heading.setStyleSheet(f'font-size:{24*factor:g}px;font-weight:650;')
        self.scene_title.setStyleSheet(f'font-size:{15*factor:g}px;font-weight:600;')
        self.setStyleSheet(f'''
            QMainWindow,QWidget {{ background:{bg}; color:{text}; font-size:{13*factor:g}px; }}
            QDockWidget::title {{ padding:10px; font-weight:600; background:{panel}; }}
            QTreeWidget,QDoubleSpinBox,QComboBox {{ background:{panel}; border:1px solid {border}; border-radius:5px; padding:5px; }}
            QPushButton {{ background:{panel}; border:1px solid {border}; border-radius:6px; padding:7px 15px; }}
            QPushButton:hover {{ border-color:#61baa8; }}
            QPushButton:disabled {{ color:{muted}; }}
            QPushButton#primary {{ background:#58cdb5; color:#10251f; font-weight:600; }}
            QPushButton#primary:disabled {{ background:{panel}; color:{muted}; }}
            QLabel#muted {{ color:{muted}; font-size:{12*factor:g}px; }}
        ''')
        self.plot.setBackground('#101925' if dark else '#eaf0f5')
        for name in ('left','bottom','right'):
            axis = self.plot.getAxis(name)
            if axis:
                axis.setPen(pg.mkPen(muted))
                axis.setTextPen(pg.mkPen(muted))

    def _theme_changed(self,theme):
        self.project = replace(self.project,display=replace(self.project.display,theme=theme))
        self.lifecycle.dirty = True
        self._apply_theme(theme)

    def _view_changed(self,view):
        self.project = replace(self.project,display=replace(self.project.display,view=view))
        self.lifecycle.dirty = True
        self._draw()

    def _contrast_changed(self,value):
        self.project = replace(self.project,display=replace(self.project.display,contrast=value))
        self.lifecycle.dirty = True
        self._draw()

    def _update_grid_label(self):
        g = self.scene.grid
        self.grid_label.setText(f'{g.nx} × {g.ny}  ·  dx {g.dx:g}  ·  dt {g.dt:g}')
        self.warning.setText(f'Estimated numerical buffers: {g.estimated_bytes/1024**2:.1f} MiB\n' + '\n'.join(self.scene.warnings))

    def _draw(self):
        g = self.scene.grid
        if self.project.display.view == 'Material':
            data = self.scene.refractive_index
            self.scale.setColorMap(pg.ColorMap([0,1],['#162331','#6cdec8']))
            self.scale.axis.setLabel('Refractive index')
            self.scale.setLevels((1,max(2,float(data.max()))))
        else:
            data = self.frame.field if self.frame is not None else np.zeros(g.shape,dtype=np.float32)
            value = self.project.display.contrast
            self.scale.setColorMap(self._field_map())
            self.scale.axis.setLabel('Field (relative)')
            self.scale.setLevels((-value,value))
        self.image.setImage(data,autoLevels=False)
        self.image.setRect(QRectF(0,0,g.width,g.height))
        source = next(o for o in self.project.objects if isinstance(o,SourceObject))
        self.source_marker.setData([source.start[0]],[source.start[1]])

    def _refresh_controls(self):
        running = self.lifecycle.state == State.RUNNING
        self.run_button.setEnabled(not running)
        self.pause_button.setEnabled(running)
        self.step_button.setEnabled(self.lifecycle.can_step)
        for box in self.inputs.values(): box.setEnabled(not running)
        self.device.setEnabled(not running)
        self.edit_hint.setVisible(running)
        self.state_label.setText(self.lifecycle.state.value)

    def _edit_source(self):
        if self._syncing or self.lifecycle.state == State.RUNNING:
            return
        values = {name:box.value() for name,box in self.inputs.items()}
        candidate = with_source(self.project,start=(values.pop('x'),values.pop('y')),**{**values,'phase':math.radians(values['phase'])})
        if candidate == self.project: return
        try:
            scene = compile_project(candidate)
        except ValueError as error:
            self.message.setText(str(error))
            source = self.project.objects[0]
            self._syncing = True
            for name,box in self.inputs.items():
                box.setValue(source.start[0] if name == 'x' else source.start[1] if name == 'y' else math.degrees(source.phase) if name == 'phase' else getattr(source,name))
            self._syncing = False
            return
        self.project,self.scene = candidate,scene
        self.lifecycle.physical_change()
        self.worker.submit('reset',self.lifecycle.identity)
        self.frame = None
        self.time_label.setText('t = 0.000  ·  0 steps')
        self.message.setText(strings.CHANGED)
        self._update_grid_label()
        self._draw()
        self._refresh_controls()

    def _device_changed(self,value):
        self.project = replace(self.project,settings=replace(self.project.settings,device=value.lower()))
        self.lifecycle.physical_change()
        self.worker.submit('reset',self.lifecycle.identity)
        self.frame = None
        self.time_label.setText('t = 0.000  ·  0 steps')
        self.message.setText(strings.CHANGED)
        self._draw()
        self._refresh_controls()

    def run_simulation(self):
        try:
            scene = compile_project(self.project)
            fresh = self.lifecycle.run()
            self.scene = scene
            self.worker.submit('start' if fresh else 'resume',self.lifecycle.identity,scene,self.project.settings.device)
            self.message.setText('Experiment running.' + ('  ' + ' '.join(scene.warnings) if scene.warnings else ''))
        except Exception as error:
            self.lifecycle.fail(str(error))
            self.message.setText(str(error))
        self._refresh_controls()

    def pause_simulation(self):
        self.lifecycle.pause()
        self.worker.submit('pause',self.lifecycle.identity)
        self.message.setText('Paused. Run resumes this experiment; Step advances one time step.')
        self._refresh_controls()

    def step_simulation(self):
        if self.lifecycle.can_step:
            self.worker.submit('step',self.lifecycle.identity)

    def reset_simulation(self):
        self.lifecycle.reset()
        self.worker.submit('reset',self.lifecycle.identity)
        self.frame = None
        self.time_label.setText('t = 0.000  ·  0 steps')
        self.message.setText(strings.READY)
        self._draw()
        self._refresh_controls()

    def _poll(self):
        result = self.worker.latest.take()
        if result is None or not self.lifecycle.accepts(result.identity): return
        if isinstance(result,Failure):
            self.lifecycle.fail(result.message)
            self.frame = None
            self.message.setText(result.message)
            self._draw()
            self._refresh_controls()
        elif isinstance(result,Frame):
            self.frame = result
            self.time_label.setText(f't = {result.time:.3f}  ·  {result.steps:,} steps')
            self._draw()

    def closeEvent(self,event):
        self.timer.stop()
        self.lifecycle.reset()
        self.worker.shutdown()
        if not self.worker.wait(5000):
            event.ignore()
            self.message.setText('Waiting for the current simulation block to finish. Close again shortly.')
            return
        event.accept()
