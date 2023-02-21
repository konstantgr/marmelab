from ..Project import PPath
import numpy as np
from src.views.Widgets.SettingsTable import QAbstractTableModel
from ..Project import PPath, PScanner
from PyQt6.QtWidgets import QWidget, QHeaderView, QHBoxLayout, QTableView, QVBoxLayout, QSizePolicy, QGroupBox, QComboBox
import numpy as np
from typing import List
from src.views.Widgets.SettingsTable import QSmartTableModel
from PyQt6.QtCore import Qt, QObject, QModelIndex
from PyQt6.QtGui import QColor
from typing import Any
from src.views.Widgets import StateDepPushButton, StateDepCheckBox
import re
from ...scanner import Position
from dataclasses import dataclass, field
import math


# TODO: в классе TableModel реализовать вызов функции set_relative
# TODO: в модели хранятся абсолютные координаты. при нажатии чекбокса данные меняются только во вьюшке. Когда пользоват.
# TODO: вводит данные, их всегда надо переводить в абослютные координаты. реализовать в setData (в модели таблицы)
# TODO: реализовать проверку в функции SetData на нажатый чекбокс(если галочка нажата, к конечным координатам прибавляем
# TODO: то, что вбил пользователь, а начальные не меняем)
# TODO: добавть во вьюшке кнопки: 1) устанавливает относительные координаты и одновременно перемещает точку начала
# TODO: сканирования в позицию сканера, 2) просто перемещает точку сканирования в позицию сканера
# TODO: траснпонировать заголовки
# TODO: добавить чекбокс с выбором измеряемых осей



@dataclass
class TableData:
    start: Position = field(default_factory=Position)
    end: Position = field(default_factory=Position)
    points: Position = field(default_factory=Position)
    step: Position = field(default_factory=Position)


class TableModel(QAbstractTableModel):
    def __init__(self, scanner: PScanner):
        super(TableModel, self).__init__()
        self.h_headers = ["x", "y", "z", "w"]
        self.axes_names = ["x", "y", "z", "w"]
        self.relative = False
        self.split_type: str = "step"
        self._data = TableData()
        self.scanner_position = Position()
        self.scanner = scanner
        self.scanner.signals.position.connect(self.update_scanner_position)

    def update_scanner_position(self, position: Position):
        self.scanner_position = position

    @property
    def v_headers(self) -> list:
        if self.split_type == "step":
            return ["Begin coordinates", "End coordinates", "Step", "Order"]
        elif self.split_type == "points":
            return ["Begin coordinates", "End coordinates", "Points", "Order"]
        else:
            raise RuntimeError("Wrong split type")

    def set_relative(self, state: bool):
        """
        реализовать вызов функции
        :param state:
        :return:
        """
        self.relative = state
        start_index = self.index(0, 0)
        end_index = self.index(1, 3)
        self.dataChanged.emit(start_index, end_index)

    def set_split_type(self, split_type: str):
        self.split_type = split_type
        self.headerDataChanged.emit(Qt.Orientation.Vertical, 0, 1)
        start_index = self.index(2, 0)
        end_index = self.index(2, 3)
        self.dataChanged.emit(start_index, end_index)

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        flags = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        flags |= Qt.ItemFlag.ItemIsEditable
        return flags

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.h_headers[section]
            else:
                return self.v_headers[section]

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        row = index.row()
        column = index.column()
        axis_name = self.axes_names[column]
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            if row == 0:
                start = self._data.start
                if self.relative:
                    start -= self.scanner_position
                return start.__getattribute__(axis_name)
            elif row == 1:
                end = self._data.end
                if self.relative:
                    end -= self.scanner_position
                return end.__getattribute__(axis_name)
            elif row == 2:
                if self.split_type == "step":
                    return self._data.step.__getattribute__(axis_name)

                elif self.split_type == "points":
                    return self._data.points.__getattribute__(axis_name)

    def match_positions(self):
        """
        функция, которая совмещает начало области измерения с положением сканера.
        :param self:
        :return:
        """
        self._data.end = self._data.end + self.scanner_position - self._data.start
        self._data.start = self.scanner_position

    def setData(self, index: QModelIndex, value: Any, role: int = ...) -> bool:
        if role == Qt.ItemDataRole.EditRole:
            row = index.row()
            column = index.column()
            axis_name = self.axes_names[column]
            if row == 0:
                self._data.start.__setattr__(axis_name, float(value))
            elif row == 1:
                self._data.end.__setattr__(axis_name, float(value))
            elif row == 2:
                start = self._data.start.__getattribute__(axis_name)
                end = self._data.end.__getattribute__(axis_name)
                if self.split_type == "step":
                    self._data.step.__setattr__(axis_name, float(value))
                    self._data.points.__setattr__(axis_name, math.floor(abs(end - start) / float(value)))
                elif self.split_type == "points":
                    self._data.points.__setattr__(axis_name, int(value))
                    self._data.step.__setattr__(axis_name, (abs(end - start) / int(value)))
            self.dataChanged.emit(index, index)
        return True


        #  использовать когда будет добавлена валидация, придумат способ проверки на координаты попроще
        # elif role == Qt.ItemDataRole.BackgroundRole:
        #     if self._data[row][column] == "":
        #         return QColor('lightgrey')
        #     # elif self._valid(self._data[row][column], self.variable):
        #         # return
        #     return QColor('red')


class TablePathModel(PPath):
    def __init__(self, name: str, scanner: PScanner):
        super(TablePathModel, self).__init__(name=name)
        self.table_model = TableModel(scanner)

    def set_relative(self, state: bool):
        self.table_model.set_relative(state)

    def set_split_type(self, split_type: str):
        self.table_model.set_split_type(split_type)

    def get_points_axes(self) -> tuple[str, ...]:
        pass

    def get_points_ndarray(self) -> np.ndarray:
        pass

    def mesh_maker(self, lst: List):
        """
        функция, которая формирует набор значений, в которых будет производиться измерения
        она выдает либо с заданным шагом, либо с фиксированным количеством точек, возможно реализовать без списка
        :param lst:
        :return:
        """
        if self.split_type == "step":
            arr = int(abs(lst[0] - lst[1] - 1) / lst[2])
            mesh = np.linspace(lst[0], lst[1], arr)
        elif self.split_type == "points":
            mesh = np.linspace(lst[0], lst[1], int(lst[2]))
        return mesh


