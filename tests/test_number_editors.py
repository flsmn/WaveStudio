"""Numeric entry stays compact without changing precise simulation settings."""
from dataclasses import replace
import os
os.environ.setdefault('QT_QPA_PLATFORM','offscreen')
import pytest
from PySide6.QtCore import QLocale,Qt
from PySide6.QtGui import QValidator
from PySide6.QtTest import QTest
from PySide6.QtWidgets import QApplication
from wave_studio.domain.project import Project
from wave_studio.ui.dialogs import SettingsDialog
from wave_studio.ui.numbers import NumberBox,IntegerBox


@pytest.fixture
def app():
    return QApplication.instance() or QApplication([])


@pytest.mark.parametrize('value,text',[(32,'32'),(.5,'0.5'),(.0002,'0.0002'),(.000001,'0.000001'),(1/60,'0.0166667')])
def test_compact_dot_decimal_display_under_german_locale(app,value,text):
    previous=QLocale()
    QLocale.setDefault(QLocale('de_DE'))
    try:
        box=NumberBox();box.setRange(-10000,10000);box.setValue(value)
        assert box.text()==text
        assert box.value()==pytest.approx(value,abs=1e-12)
        assert box.validate('0,5',3)[0]==QValidator.State.Invalid
        integer=IntegerBox();integer.setRange(0,10000);integer.setValue(1234)
        assert integer.text()=='1234'
    finally:
        QLocale.setDefault(previous)


@pytest.mark.parametrize('value,smaller',[(1,.99),(.5,.49),(.05,.049),(.0002,.00019)])
def test_arrows_use_small_reversible_steps_below_one(app,value,smaller):
    box=NumberBox();box.setRange(.000001,100);box.setValue(value)
    box.stepDown();assert box.value()==pytest.approx(smaller)
    box.stepUp();assert box.value()==pytest.approx(value)


def test_unchanged_rounded_display_preserves_precise_spacing(app):
    box=NumberBox();box.setRange(.000001,100);box.setValue(1/60);box.show()
    try:
        app.processEvents();precise=box.value()
        assert box.text()=='0.0166667'
        box.setFocus();QTest.keyClick(box,Qt.Key.Key_Return);app.processEvents()
        assert box.value()==precise
        box.interpretText();assert box.value()==precise
    finally:box.close()


def test_user_can_replace_rounded_display_with_exact_value(app):
    box=NumberBox();box.setRange(.000001,100);box.setValue(.9999999);box.show()
    try:
        assert box.text()=='1'
        box.lineEdit().selectAll();QTest.keyClicks(box,'1')
        QTest.keyClick(box,Qt.Key.Key_Return)
        assert box.value()==1
        box.lineEdit().selectAll();QTest.keyClicks(box,'0.125')
        QTest.keyClick(box,Qt.Key.Key_Return)
        assert box.value()==.125 and box.text()=='0.125'
    finally:box.close()
