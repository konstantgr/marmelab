from PyQt6.QtWidgets import QAbstractItemView, QFrame, QWidget, QTableView, QGroupBox, QHBoxLayout, QGridLayout, QSizePolicy, QHeaderView, QPushButton, QVBoxLayout
from PyQt6.QtWidgets import QLabel, QLineEdit
from PyQt6.QtCore import Qt, QAbstractTableModel
from PyQt6 import QtCore
from PyQt6.QtGui import QColor
from src.Variable import Setting, Variable
from typing import Union, Any, Callable
import re
from PyQt6.QtCore import QObject
from dataclasses import dataclass
from .StatedependentButton import StateDepPushButton
from src.project.Project import PState
from PyQt6.QtCore import pyqtBoundSignal, pyqtSignal, QObject
from functools import partial


class Signals(QObject):
    user_input_changed: pyqtBoundSignal = pyqtSignal(str)


class Model:
    def __init__(self, keys: list[str]):
        self._keys = keys
        self._user_inputs = {key: '' for key in keys}
        self.signals = Signals()

    def keys(self) -> list[str]:
        """Возвращает наименования полей"""
        return self._keys

    def get_parsed_value(self, key: str) -> float or None:
        """Возвращает пропаршенные значения"""
        try:
            res = float(self._user_inputs[key])
        except:
            res = None
        return res

    def set_user_input(self, key: str, input: str):
        """Установить значение, введенное пользователем"""
        self._user_inputs[key] = input
        self.signals.user_input_changed.emit(key)

    def get_user_input(self, key: str) -> str:
        """Возвращает значения, введенные пользоватем"""
        return self._user_inputs[key]


class View(QWidget):
    def __init__(self, model: Model, *args, **kwargs):
        super(View, self).__init__(*args, **kwargs)
        layout = QGridLayout()
        self.setLayout(layout)
        self.model = model
        self.keys: list[str] = []
        self.inputs: list[QLineEdit] = []
        self.outputs: list[QLabel] = []

        for i, key in enumerate(model.keys()):
            label = QLabel(key + ':')
            layout.addWidget(label, i, 0, 1, 1, Qt.AlignmentFlag.AlignRight)
            self.keys.append(key)
            label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)

            input_widget = QLineEdit(self.model.get_user_input(key))
            layout.addWidget(input_widget, i, 1, 1, 1, Qt.AlignmentFlag.AlignHCenter)
            self.inputs.append(input_widget)
            input_widget.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)

            def kek(key: str):
                def mem(text: str):
                    self.model.set_user_input(key=key, input=text)
                return mem
            input_widget.textChanged.connect(kek(key))

            output_widget = QLabel()
            layout.addWidget(output_widget, i, 2, 1, 1, Qt.AlignmentFlag.AlignLeft)
            self.outputs.append(output_widget)
            self.update_output(key)
            output_widget.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)

        self.model.signals.user_input_changed.connect(self.update_output)

    def update_output(self, key: str):
        i = self.keys.index(key)
        self.outputs[i].setText(self.format_parse(self.model.get_parsed_value(key)))

    @staticmethod
    def format_parse(output: str) -> str:
        """Форматирование вывода"""
        return '->' + str(output)

