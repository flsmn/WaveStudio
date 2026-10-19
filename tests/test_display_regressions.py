"""Display regressions; Qt checks are not native accessibility acceptance."""
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


def test_paused_rates_remain_zero_after_acknowledgement(window):
    from wave_studio.simulation.worker import Frame
    w=window;w.lifecycle.run();w._rates.observe(1,time.monotonic()-2);w.lifecycle.pause()
    w.worker.latest.put(Frame(w.lifecycle.identity,1,240,None,paused=True))
    w._refresh_controls();w._poll()
    assert w.rate_label.text()=='0 steps/s · 0 frames/s'



def test_two_views_preserve_units_and_camera_on_display_change(window):
    w=window;w.secondary_action.setChecked(True);QApplication.processEvents()
    w.splitter.setSizes([250,500]);QApplication.processEvents()
    w.plot.setRange(xRange=(2,22),yRange=(4,24),padding=0);QApplication.processEvents()
    a,b=w.plot.getViewBox(),w.second.getViewBox()
    assert a.viewPixelSize()[0]==pytest.approx(b.viewPixelSize()[0],rel=.01)
    assert a.viewPixelSize()[0]==pytest.approx(a.viewPixelSize()[1],rel=.01)
    assert b.viewPixelSize()[0]==pytest.approx(b.viewPixelSize()[1],rel=.01)
    sizes=w.splitter.sizes();w.theme.setCurrentText('Light');assert w.splitter.sizes()==sizes
    w.second.setRange(xRange=(8,18),yRange=(8,18),padding=0);QApplication.processEvents()
    assert a.viewPixelSize()[0]==pytest.approx(b.viewPixelSize()[0],rel=.01)



def test_large_text_controls_and_dialog_buttons_stay_accessible(window,tmp_path):
    w=window;w.resize(980,660)
    for theme in ('Dark','Light'):
        for scale in (1.,1.25,1.5):
            assert w.commit(replace(w.project,display=replace(w.project.display,theme=theme,text_scale=scale)))
            QApplication.processEvents()
            for button in (w.run_button,w.pause_button,w.step_button,w.reset_button):
                assert w.centralWidget().rect().contains(button.mapTo(w.centralWidget(),button.rect().bottomRight()))
            assert w.run_button.font().pixelSize()==round(13*scale)
            w.grab().save(str(tmp_path/f'{theme}-{scale}.png'))
            d=ObjectDialog(DetectorObject(),lambda o:None,w);d.show();QApplication.processEvents()
            for button in d.findChild(QDialogButtonBox).buttons():assert d.rect().contains(button.mapTo(d,button.rect().bottomRight()))
            d.close()



def test_geometric_tools_convert_screen_points_at_two_zoom_levels(window):
    from PySide6.QtCore import Qt,QPointF
    w=window
    class Event:
        def __init__(self,p):self.p=p
        def button(self):return Qt.MouseButton.LeftButton
        def scenePos(self):return w.plot.getViewBox().mapViewToScene(QPointF(*self.p))
    for extent in (32,16):
        w.plot.setRange(xRange=(0,extent),yRange=(0,extent),padding=0);QApplication.processEvents()
        w.start_measure('distance')
        for point in ((3,4),(6,8)):w.canvas_click(Event(point))
        assert w.message.text()=='Distance: 5.00000 reference lengths'
        w.start_measure('angle')
        for point in ((3,4),(6,4),(6,8)):w.canvas_click(Event(point))
        assert w.message.text()=='Angle: 90.000°'



def test_large_text_minimum_window_with_two_views_and_long_counters(window):
    w=window
    w.commit(replace(w.project,display=replace(w.project.display,text_scale=1.5,secondary_visible=True,theme='Light')))
    w.time_label.setText('t = 1284.250 · 20,548 steps');w.state_label.setText('Paused')
    w.resize(980,660);QApplication.processEvents()
    assert w.size().width()==980 and w.size().height()==660
    for chart in (w.plot,w.second,w.profile_plot):
        assert chart.getAxis('bottom').labelStyle['color']=='#42566b'
    for chart in (w.plot,w.second):
        assert chart.getAxis('bottom').labelText=='x' and chart.getAxis('left').labelText=='y'
        assert chart.getAxis('bottom').labelUnits==chart.getAxis('left').labelUnits=='reference length'
    assert w.profile_plot.getPlotItem().legend.opts['labelTextColor']=='#42566b'
    from wave_studio.simulation.lifecycle import State
    w.state_label.setText(State.CHANGED.value);QApplication.processEvents()
    for label in (w.state_label,w.time_label,w.rate_label):
        assert w.centralWidget().rect().contains(label.mapTo(w.centralWidget(),label.rect().bottomRight()))



def test_completed_profile_redraws_only_when_visible_data_changes(window,monkeypatch):
    import torch
    from wave_sim2d.measurements import Measurements
    w=window;d=DetectorObject(samples=2,settling=0,window=1)
    w.replace_project(Project(detectors=(d,)))
    measurements=Measurements(w.scene.grid,'cpu');measurements.configure(w.detector_specs(),0)
    field=torch.ones(w.scene.grid.shape)
    for i in range(16):measurements.update(field,(i+1)*w.scene.grid.dt,w.scene.grid.dt)
    profile=measurements.results()[d.id];w.profiles[d.id]=profile;w._plot_profiles()
    clears=[];original=w.profile_plot.clear
    def clear():clears.append(1);original()
    monkeypatch.setattr(w.profile_plot,'clear',clear)
    for _ in range(10):w._plot_profiles()
    assert clears==[]
    w.profiles[d.id]={**profile,'metadata':{'time':99}};w._plot_profiles();assert clears==[]
    w.profiles[d.id]={**profile,'values':[.25,.5]};w._plot_profiles();assert len(clears)==1
    w.norm.setCurrentText('Shared maximum = 1');assert len(clears)==2
    w.theme.setCurrentText('Light');assert len(clears)==3
