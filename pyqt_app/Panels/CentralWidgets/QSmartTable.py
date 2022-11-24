from PyQt6.QtWidgets import QTableWidget, QWidget, QItemDelegate, QLineEdit, QTableWidgetItem, QSizePolicy, QTableView, QStyledItemDelegate, QStyleOptionViewItem, QHeaderView
from PyQt6.QtCore import Qt, QAbstractTableModel
from PyQt6 import QtCore
from PyQt6.QtGui import QColor, QValidator
from PyQt6 import QtGui, QtWidgets
from dataclasses import dataclass
from typing import Union, Type, Any
import re
from PyQt6.QtCore import pyqtSignal, pyqtBoundSignal, QObject

STANDARD_UNIT_PREFIXES = {
    'n': 1e-9,
    'u': 1e-6,
    'm': 1e-3,
    'c': 1e-2,
    'd': 1e-1,
    '': 1,
    'k': 1e3,
    'M': 1e6,
    'G': 1e9,
    'T': 1e12,
}


class Unit():
    """
    Класс единицы измерения
    """
    unit_base = 'm'
    program_used_unit_prefix = 'm'

    @classmethod
    def validate(cls, unit: str) -> bool:
        """
        Функция, которая проверяет соответствие введенной строки данной единице измерения

        :param unit: единица измерения
        :return:
        """
        if not unit.endswith(cls.unit_base):
            return False
        if unit[:-len(cls.unit_base)] not in STANDARD_UNIT_PREFIXES.keys():
            return False
        return True

    @classmethod
    def to_default_unit(cls, value: float, unit: str) -> float:
        """
        Функция, которая принимает число и единицу измерения и переводит в единицы, используемые в программе
        (мм, с, град, Гц)

        :param value: единица измерения
        :param unit: значение
        :return:
        """
        value_in_standart_unit = value * STANDARD_UNIT_PREFIXES[unit[:-len(cls.unit_base)]]
        return value_in_standart_unit / STANDARD_UNIT_PREFIXES[cls.program_used_unit_prefix]

    @classmethod
    def default_unit(cls) -> str:
        """
        Возвращает единицу измерения, используемую в программе

        :return:
        """
        return cls.program_used_unit_prefix + cls.program_used_unit_prefix


class Length(Unit):
    unit_base = 'm'
    program_used_unit_prefix = 'm'


class Time(Unit):
    unit_base = 's'
    program_used_unit_prefix = ''


class Frequency(Unit):
    unit_base = 'Hz'
    program_used_unit_prefix = ''


class NoUnit(Unit):
    unit_base = ''
    program_used_unit_prefix = ''

    @classmethod
    def validate(cls, unit: str) -> bool:
        return unit == cls.unit_base


@dataclass
class Variable:
    """
    Класс переменной для таблицы
    """
    name: str
    default_value: Union[int, float]
    type: Union[Type[int], Type[float]]
    unit: Type[Unit] = NoUnit
    description: str = ''


class QSmartTableModel(QAbstractTableModel):
    """
    Реализация Модели
    """
    def __init__(self, variables: list[Variable], parent: QObject = None):
        super().__init__(parent)
        self.variables = variables
        self._data = [str(var.default_value) for var in variables]
        self.headers = ['Variable', 'Value', 'Unit', 'Description']
        self.pattern = re.compile(r"^\d+(?:\.\d+)?\s*(?:\[\s*[a-zA-Z]*\s*])?$")

    def rowCount(self, parent: QtCore.QModelIndex = ...) -> int:
        return len(self._data)

    def columnCount(self, parent: QtCore.QModelIndex = ...) -> int:
        return len(self.headers)

    def data(self, index: QtCore.QModelIndex, role: int = ...) -> Any:
        row = index.row()
        column = index.column()
        variable = self.variables[row]
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            if column == 0:
                return variable.name
            elif column == 1:
                return self._data[row]
            elif column == 2:
                if self._valid(self._data[row], variable):
                    _, unit = self._value_str_and_unit(self._data[row], variable)
                    return unit
                return variable.unit.default_unit()
            elif column == 3:
                return variable.description
        if role == Qt.ItemDataRole.ToolTipRole:
            if column == 3:
                return variable.description
        elif role == Qt.ItemDataRole.BackgroundRole:
                if self._valid(self._data[row], variable):
                    return
                return QColor('red')

    @staticmethod
    def _value_str_and_unit(text: str, variable: Variable):
        """
        Принимает текст " 123.2 [ xy ] ", преобразует его в ("123.2", "xy").
        В случае " 123.2", преобразует текст в ("123.2", "xy"), где "xy" -- дефолтные единицы измерения переменной.

        :param text:
        :param variable:
        :return:
        """
        text = text.strip()
        if text.count('['):
            value, unit = text[:-1].split('[')
            return value.strip(), unit.strip()
        else:
            return text.strip(), variable.unit.default_unit()

    def _valid(self, value: str, variable: Variable):
        """
        Проверяет валидность введенного текста

        :param value:
        :param variable:
        :return:
        """
        text = value.strip()
        if not re.match(self.pattern, text):
            return False

        value_str, unit = self._value_str_and_unit(text, variable)

        if not variable.unit.validate(unit):
            return False

        try:
            variable.type(value_str)
        except:
            return False

        return True

    def flags(self, index: QtCore.QModelIndex) -> Qt.ItemFlag:
        flags = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        if index.column() == 1:
            flags |= Qt.ItemFlag.ItemIsEditable
        return flags

    def setData(self, index: QtCore.QModelIndex, value: Any, role: int = ...) -> bool:
        if role == Qt.ItemDataRole.EditRole:
            row = index.row()
            self._data[row] = value

            for i in range(len(self.headers)):
                unit_cell_index = index.sibling(0, i-1)
                self.dataChanged.emit(unit_cell_index, unit_cell_index)
        return True

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.headers[section]

    def to_dict(self):
        res = {}
        for i in range(len(self.variables)):
            text = self._data[i]
            variable = self.variables[i]
            try:
                value_str, unit = self._value_str_and_unit(text, variable)
                value = variable.unit.to_default_unit(variable.type(value_str), unit)
                res[variable.name] = value
            except Exception as e:
                raise e
        return res

    def set_default(self):
        for i, variable in enumerate(self.variables):
            index = self.index(i, 1)
            self.setData(index, str(variable.default_value), Qt.ItemDataRole.EditRole)


class QSmartTable(QTableView):
    """
    Реализация умной таблицы
    """

    valid: pyqtBoundSignal = pyqtSignal(bool)

    def __init__(self, variables: list[Variable], parent: QWidget = None):
        super(QSmartTable, self).__init__(parent)
        self.setModel(QSmartTableModel(variables))

        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)

    def to_dict(self):
        model: QSmartTableModel = self.model()
        return model.to_dict()

    def set_default(self):
        model: QSmartTableModel = self.model()
        model.set_default()
