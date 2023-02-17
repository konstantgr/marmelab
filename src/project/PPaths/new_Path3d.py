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
from dataclasses import dataclass


# TODO: в классе TableModel реализовать вызов функции set_relative


@dataclass
class Axis:
    start: float = None
    end: float = None
    points: int = None
    step: float = None


class TableModel(QAbstractTableModel):
    def __init__(self):
        super(TableModel, self).__init__()
        self.h_headers = ["x", "y", "z", "w"]
        self.relative = False
        self.split_type: str = "step"
        self._data = [Axis(), Axis(), Axis(), Axis()]

    @property
    def v_header(self) -> list:
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

    def set_split_type(self, split_type: str):
        self.split_type = split_type
        self.headerDataChanged.emit(Qt.Orientation.Vertical, 0, 1)

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.h_headers[section]
            else:
                return self.v_headers[section]


class ToyPath(PPath):
    def __init__(self, name: str):
        super(ToyPath, self).__init__(name=name)
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


