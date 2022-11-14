from PyQt6.QtWidgets import QTableWidget, QWidget, QItemDelegate, QLineEdit, QTableWidgetItem, QSizePolicy
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QValidator
from dataclasses import dataclass
from typing import Union, Type
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
class Setting:
    var_name: str
    units: Type[Unit]
    default_value: float
    description: str
    type: Union[Type[int], Type[float], Type[bool]]


class QSmartTableItem(QTableWidgetItem):
    def __init__(self, text: str, setting: Setting):
        super(QSmartTableItem, self).__init__(text)
        self.setting = setting
        self.valid = True


class QSmartTable(QTableWidget):
    """
    Реализация умной таблицы
    """

    acceptable_table: pyqtBoundSignal = pyqtSignal(bool)

    def __init__(self, settings: list[Setting], parent: QWidget = None):
        super(QSmartTable, self).__init__(len(settings), 4, parent)
        self.settings = settings
        self.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum))
        self.value_items = []

        for i, setting in enumerate(self.settings):
            name_item = QTableWidgetItem(setting.var_name)
            name_item.setFlags(Qt.ItemFlag.ItemIsEditable)
            name_item.setForeground(QColor('gray'))
            self.setItem(i, 0, name_item)

            value_item = QSmartTableItem(str(setting.default_value), setting)
            self.value_items.append(value_item)
            self.setItem(i, 1, value_item)

            units_item = QTableWidgetItem(setting.units.default_unit())
            units_item.setFlags(Qt.ItemFlag.ItemIsEditable)
            units_item.setForeground(QColor('gray'))
            self.setItem(i, 2, units_item)

            description_item = QTableWidgetItem(setting.description)
            description_item.setFlags(Qt.ItemFlag.ItemIsEditable)
            description_item.setForeground(QColor('gray'))
            self.setItem(i, 3, description_item)

        self.setHorizontalHeaderLabels(['name', 'value', 'units', 'description'])
        self.itemChanged.connect(self.checkData)

        self.pattern = re.compile(r"^\d+(?:\.\d+)?(?:\[[a-zA-Z]*\])?$")

    def checkData(self, item: QSmartTableItem):
        text = item.text().strip()
        print(item.text())
        if not re.match(self.pattern, text):
            item.setBackground(QColor('red'))
            item.valid = False
            self.acceptable_table.emit(False)
            return False

        if text.count('['):
            value_str, units = text[:-1].split('[')
            value = item.setting.type(value_str)
        else:
            units = item.setting.units.default_unit()
            value = item.setting.type(text)

        if not item.setting.units.validate(units):
            item.setBackground(QColor('red'))
            item.valid = False
            self.acceptable_table.emit(False)
            return False

        item.setBackground(QColor('white'))
        item.valid = True
        self.item(item.row(), item.column()+1).setText(units)
        self.acceptable_table.emit(all([x.valid for x in self.value_items]))
        return True
