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
                if self.split_type == "step":
                    self._data.step.__setattr__(axis_name, float(value))

            self.dataChanged.emit(index, index)
            # self.headerDataChange  использовать в другой функции
        return True


        #  использовать когда будет добавлена валидация, придумат способ проверки на координаты попроще
        # elif role == Qt.ItemDataRole.BackgroundRole:
        #     if self._data[row][column] == "":
        #         return QColor('lightgrey')
        #     # elif self._valid(self._data[row][column], self.variable):
        #         # return
        #     return QColor('red')


class TablePathModel(PPath):
    def __init__(self, name: str):
        super(TablePathModel, self).__init__(name=name)
        self.x_min = None
        self.y_min = None
        self.p = None
        self.y_max = None
        self.x_points = None
        self.y_points = None

    def set_lims(self, x_min, x_max, y_min, y_max, x_points, y_points):
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max
        self.x_points = x_points
        self.y_points = y_points

    def get_points_axes(self) -> tuple[str, ...]:
        return "y", "x"

    def get_points_ndarray(self) -> np.ndarray:
        res = []
        xs = np.linspace(self.x_min, self.x_max, self.x_points, dtype=float)
        ys = np.linspace(self.y_min, self.y_max, self.y_points, dtype=float)

        for i in range(len(xs)):
            for j in range(len(ys)):
                if i % 2 == 0:
                    res.append([xs[i], ys[j]])
                else:
                    res.append([xs[i], ys[-j-1]])
        return np.array(res)


