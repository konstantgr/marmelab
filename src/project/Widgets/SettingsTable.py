from PyQt6.QtWidgets import QWidget, QTableView, QSplitter, QHBoxLayout, QSizePolicy, QHeaderView, QPushButton, QVBoxLayout
from PyQt6.QtCore import Qt, QAbstractTableModel
from PyQt6 import QtCore
from PyQt6.QtGui import QColor
from ..Variable import Setting, Unit, Variable
from typing import Union, Any
import re
from PyQt6.QtCore import QObject
from dataclasses import dataclass


@dataclass
class ModelVariable(Variable):
    """
    В value хранится введенное пользователем значение
    """
    value: str = ""
    default_value: Union[float, int] = None


class QSmartTableModel(QAbstractTableModel):
    """
    Реализация Модели
    """
    def __init__(self, settings: list[Setting], parent: QObject = None):
        super().__init__(parent)
        self.settings = settings
        self._data = [
            ModelVariable(
                name=setting.name,
                unit=setting.unit,
                value=str(setting.default_value),
                description=setting.description,
                type=setting.type,
                default_value=setting.default_value
            ) for setting in settings
        ]
        self.headers = ['Variable', 'Value', 'Unit', 'Description']
        self._pattern = re.compile(r"^\d+(?:\.\d+)?\s*(?:\[\s*[a-zA-Z]*\s*])?$")

    def rowCount(self, parent: QtCore.QModelIndex = ...) -> int:
        return len(self.settings)

    def columnCount(self, parent: QtCore.QModelIndex = ...) -> int:
        return len(self.headers)

    def data(self, index: QtCore.QModelIndex, role: int = ...) -> Any:
        row = index.row()
        column = index.column()
        variable = self._data[row]
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            if column == 0:
                return variable.name
            elif column == 1:
                return variable.value
            elif column == 2:
                if self._validate(variable.value, variable.unit):
                    return str(variable.unit)
                return str(variable.unit)
            elif column == 3:
                return variable.description
        elif role == Qt.ItemDataRole.ToolTipRole:
            if column == 3:
                return variable.description
        elif role == Qt.ItemDataRole.BackgroundRole:
            if self._validate(variable.value, variable.unit):
                return
            return QColor('red')

    # @staticmethod
    # def _value_str_and_unit(text: str, variable: Variable):
    #     """
    #     Принимает текст " 123.2 [ xy ] ", преобразует его в ("123.2", "xy").
    #     В случае " 123.2", преобразует текст в ("123.2", "xy"), где "xy" -- дефолтные единицы измерения переменной.
    #
    #     :param text:
    #     :param variable:
    #     :return:
    #     """
    #     text = text.strip()
    #     if text.count('['):
    #         value, unit = text[:-1].split('[')
    #         return value.strip(), unit.strip()
    #     else:
    #         return text.strip(), variable.unit.default_unit()

    def _validate(self, value: str, unit: Unit):
        """
        Проверяет валидность введенного текста

        :param value:
        :param unit:
        :return:
        """
        text = value.strip()
        if not re.match(self._pattern, text):
            return False
        #
        # value_str, unit = self._value_str_and_unit(text, variable)
        #
        # if not variable.unit.validate(unit):
        #     return False
        #
        # try:
        #     variable.type(value_str)
        # except:
        #     return False

        return True

    def flags(self, index: QtCore.QModelIndex) -> Qt.ItemFlag:
        flags = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        if index.column() == 1:
            flags |= Qt.ItemFlag.ItemIsEditable
        return flags

    def setData(self, index: QtCore.QModelIndex, value: Any, role: int = ...) -> bool:
        if role == Qt.ItemDataRole.EditRole:
            row = index.row()
            variable = self._data[row]
            variable.value = value

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
        for i in range(len(self._data)):
            variable = self._data[i]
            res[variable.name] = variable.type(variable.value)
        return res

    def set_default(self):
        for i, variable in enumerate(self._data):
            index = self.index(i, 1)
            self.setData(index, str(variable.default_value), Qt.ItemDataRole.EditRole)


class QSmartTableView(QTableView):
    """
    Реализация умной таблицы
    """
    def __init__(self, settings: list[Setting], parent: QWidget = None):
        super(QSmartTableView, self).__init__(parent)
        self._model = QSmartTableModel(settings=settings, parent=self)
        self.setModel(self._model)

        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)

    def to_dict(self):
        return self._model.to_dict()

    def set_default(self):
        self._model.set_default()


class SettingsTableWidget(QWidget):
    """
    Виджет таблицы с кнопками
    """
    def __init__(
            self,
            settings: list[Setting],
            **kwargs
    ):
        super(SettingsTableWidget, self).__init__(**kwargs)

        self.splitter = QSplitter(orientation=Qt.Orientation.Vertical, parent=self)
        self.setLayout(QVBoxLayout())
        self.layout().addWidget(self.splitter)
        self.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        self.default_settings = settings

        self.table = QSmartTableView(settings=settings, parent=self.splitter)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        self.table.horizontalHeader().setStretchLastSection(True)
        # self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        # self.table.setFixedHeight(340)
        self.table.resizeRowsToContents()

        buttons_widget = QWidget(parent=self.splitter)
        buttons_widget.setLayout(QHBoxLayout())
        buttons_widget.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        # buttons_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        set_default_button = QPushButton("Set default", parent=buttons_widget)
        set_default_button.clicked.connect(self.table.set_default)
        set_default_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        buttons_widget.layout().addWidget(set_default_button)

        apply_button = QPushButton("Apply", parent=buttons_widget)
        apply_button.clicked.connect(self.apply)
        apply_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        buttons_widget.layout().addWidget(apply_button)
        buttons_widget.layout().setStretch(0, 1)
        buttons_widget.layout().setStretch(1, 1)

        self.splitter.addWidget(self.table)
        self.splitter.addWidget(buttons_widget)
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)

    def apply(self):
        """
        Применить настройки из таблицы
        """
        pass
