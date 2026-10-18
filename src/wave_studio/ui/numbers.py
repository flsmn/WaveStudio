"""Compact English numeric editors with value-dependent arrow steps."""
import math
from PySide6.QtCore import QLocale
from PySide6.QtGui import QValidator
from PySide6.QtWidgets import QAbstractSpinBox,QDoubleSpinBox,QSpinBox


def english_locale():
    locale=QLocale('en_US')
    locale.setNumberOptions(QLocale.NumberOption.RejectGroupSeparator)
    return locale


class NumberBox(QDoubleSpinBox):
    def __init__(self,parent=None):
        self._user_edited=False
        super().__init__(parent)
        self.setLocale(english_locale())
        self.setDecimals(12)
        self.setGroupSeparatorShown(False)
        self.setKeyboardTracking(False)
        self.setStepType(QAbstractSpinBox.StepType.AdaptiveDecimalStepType)
        self.lineEdit().textEdited.connect(self._mark_edited)
        self.editingFinished.connect(self._finish_edit)

    def _mark_edited(self,*args):self._user_edited=True
    def _finish_edit(self):self._user_edited=False

    def textFromValue(self,value):
        places=min(self.decimals(),max(0,5-math.floor(math.log10(abs(value))))) if value else 0
        text=f'{value:.{places}f}'
        return text.rstrip('0').rstrip('.') if '.' in text else text

    def valueFromText(self,text):
        # A rounded display must not change precise preset spacing on focus/Enter.
        if not self._user_edited and text.strip()==self.textFromValue(self.value()):
            return self.value()
        return super().valueFromText(text)

    def validate(self,text,pos):
        if ',' in text:return QValidator.State.Invalid,text,pos
        return super().validate(text,pos)

    def setValue(self,value):
        super().setValue(value);self._user_edited=False

    def stepBy(self,steps):
        super().stepBy(steps);self._user_edited=False


class IntegerBox(QSpinBox):
    def __init__(self,parent=None):
        super().__init__(parent)
        self.setLocale(english_locale())
        self.setGroupSeparatorShown(False)
        self.setKeyboardTracking(False)
