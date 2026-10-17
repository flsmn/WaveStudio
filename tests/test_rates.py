import pytest
from wave_studio.simulation.rates import FrameRates


def test_startup_and_duplicate_snapshots_do_not_bias_rates():
    r=FrameRates()
    assert r.observe(0,5) is None and r.observe(0,20) is None
    assert r.observe(1,25) is None
    for i in range(1,20):
        assert r.observe(1+i,25+i/20) is None
        assert r.observe(1+i,25+i/20+.001) is None
    assert r.observe(21,26)==pytest.approx((20,20))


def test_resume_excludes_time_spent_paused():
    r=FrameRates();r.observe(100,1);assert r.observe(120,2)==(20,1)
    r.reset();assert r.observe(120,100) is None
    for i in range(1,20):r.observe(120+i,100+i/20)
    assert r.observe(140,101)==pytest.approx((20,20))


def test_editor_starts_measurement_at_progress_and_restarts_after_resume(tmp_path,monkeypatch):
    import os
    os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
    from PySide6.QtWidgets import QApplication
    from wave_studio.ui.editor import MainWindow
    from wave_studio.simulation.worker import Frame
    import wave_studio.ui.editor as editor
    monkeypatch.setenv('WAVESTUDIO_RECOVERY_DIR',str(tmp_path))
    app=QApplication.instance() or QApplication([]);w=MainWindow();clock=[0.]
    monkeypatch.setattr(editor,'monotonic',lambda:clock[0]);monkeypatch.setattr(w.worker,'submit',lambda *args,**kwargs:None)
    def frame(steps,now):
        clock[0]=now;w.worker.latest.put(Frame(w.lifecycle.identity,steps/16,steps,None));w._poll()
    try:
        w.run_simulation();frame(0,10);assert w.rate_label.text()=='Measuring rate…'
        frame(1,11);frame(21,12);assert w.rate_label.text()=='20 steps/s · 1 frames/s'
        w.pause_simulation();assert w.rate_label.text()=='0 steps/s · 0 frames/s'
        clock[0]=100;w.run_simulation();assert w.rate_label.text()=='Measuring rate…'
        frame(22,101);frame(42,102);assert w.rate_label.text()=='20 steps/s · 1 frames/s'
    finally:w.lifecycle.dirty=False;w.close();app.processEvents()
