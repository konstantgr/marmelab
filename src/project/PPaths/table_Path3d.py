from ..Project import PPath, ProjectType
from PyQt6.QtCore import pyqtBoundSignal, pyqtSignal, QObject
from typing import Union
import numpy as np
from src.views.Widgets.SettingsTable import QAbstractTableModel
from ..Project import PPath, PScanner
from PyQt6.QtCore import Qt, QObject, QModelIndex
from PyQt6 import QtGui
from typing import Any
from ...scanner import Position
from dataclasses import dataclass, field
import math
from enum import IntEnum, auto
import time


class RowNumber(IntEnum):
    start: int = 0
    end: int = 1
    step_split: int = 2
    order: int = 3
    enable_disable_status: int = 4

@dataclass
class TableData:
    order: Position = field(default_factory=Position)
    enable_disable_status: Position = field(default_factory=Position)
    start: Position = field(default_factory=Position)
    end: Position = field(default_factory=Position)
    points: Position = field(default_factory=Position)
    step: Position = field(default_factory=Position)


class TableModelSignals(QObject):
    data_changed: pyqtBoundSignal = pyqtSignal()


class TableModel(QAbstractTableModel):
    def __init__(self, scanner: PScanner):
        super(TableModel, self).__init__()
        self.h_headers = ["x", "y", "z", "w"]
        self.axes_names = ["x", "y", "z", "w"]
        self.relative = False
        self.split_type: str = "points"
        self._data = TableData()
        self._data.order.x = 0
        self._data.order.y = 1
        self._data.order.z = 2
        self._data.order.w = 3

        self._data.start.x = self._data.start.y = self._data.start.z = self._data.start.w = 0
        self._data.end.x = self._data.end.y = self._data.end.z = self._data.end.w = 1000
        self._data.step.x = self._data.step.y = self._data.step.z = 100
        self._data.step.w = 1000
        self._data.points.x = self._data.points.y = self._data.points.z = 10
        self._data.points.w = 1

        self._data.enable_disable_status.x = self._data.enable_disable_status.y = self._data.enable_disable_status.z = 1
        self._data.enable_disable_status.w = 1

        self.scanner_position = Position()
        self.scanner = scanner
        self.signals = TableModelSignals()
        self.scanner.signals.position.connect(self.update_scanner_position)

    def update_scanner_position(self, position: Position):
        self.scanner_position = position

    @property
    def v_headers(self) -> list:
        if self.split_type == "step":
            return ["Begin coordinates", "End coordinates", "Step", "Order", "Status"]
        elif self.split_type == "points":
            return ["Begin coordinates", "End coordinates", "Points", "Order", "Status"]
        else:
            raise RuntimeError("Wrong split type")

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self.v_headers)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return len(self.h_headers)

    def set_relative(self, state: bool):
        """
        реализовать вызов функции
        :param state:
        :return:
        """
        self.relative = state
        start_index = self.index(RowNumber.start, 0)
        end_index = self.index(RowNumber.end, len(self.v_headers) - 1)
        self.dataChanged.emit(start_index, end_index)
        self.signals.data_changed.emit()

    def set_split_type(self, split_type: str):
        self.split_type = split_type
        self.headerDataChanged.emit(Qt.Orientation.Vertical, 0, 1)
        start_index = self.index(RowNumber.step_split, 0)
        end_index = self.index(RowNumber.step_split, len(self.v_headers) - 1)
        self.dataChanged.emit(start_index, end_index)
        self.signals.data_changed.emit()

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
            if row == RowNumber.start:
                start = self._data.start
                if self.relative:
                    start -= self.scanner_position
                return start.__getattribute__(axis_name)
            elif row == RowNumber.end:
                end = self._data.end
                if self.relative:
                    end -= self.scanner_position
                return end.__getattribute__(axis_name)
            elif row == RowNumber.step_split:
                if self.split_type == "step":
                    return self._data.step.__getattribute__(axis_name)

                elif self.split_type == "points":
                    return self._data.points.__getattribute__(axis_name)
            elif row == RowNumber.order:
                return self._data.order.__getattribute__(axis_name)
            elif row == RowNumber.enable_disable_status:
                return self._data.enable_disable_status.__getattribute__(axis_name)

        if role == Qt.ItemDataRole.BackgroundRole:
            if row == RowNumber.order:
                chek_lst = self._data.order.x, self._data.order.y, self._data.order.z, self._data.order.w
                if set(chek_lst) != {0, 1, 2, 3}:
                    return QtGui.QColor('#FF0000')
                else:
                    return None
            if row == RowNumber.enable_disable_status:

                chek_staus_lst = self._data.enable_disable_status.x, \
                                     self._data.enable_disable_status.y,\
                                     self._data.enable_disable_status.z, \
                                     self._data.enable_disable_status.w

                for i in chek_staus_lst:
                    if i not in (1, 0):
                        return QtGui.QColor('#FF0000')


    def match_positions(self):
        """
        функция, которая совмещает начало области измерения с положением сканера.
        :param self:
        :return:
        """
        delta = self.scanner_position - self._data.start
        self._data.end += delta
        self._data.start += delta
        start_index = self.index(RowNumber.start, 0)
        end_index = self.index(RowNumber.end, len(self.v_headers) - 1)
        self.dataChanged.emit(start_index, end_index)
        self.signals.data_changed.emit()

    def setData(self, index: QModelIndex, value: Any, role: int = ...) -> bool:
        if role == Qt.ItemDataRole.EditRole:
            row = index.row()
            column = index.column()
            axis_name = self.axes_names[column]
            if row == RowNumber.start:
                start = float(value)
                if self.relative:
                    start += self.scanner_position.__getattribute__(axis_name)
                self._data.start.__setattr__(axis_name, start)
            elif row == RowNumber.end:
                end = float(value)
                if self.relative:
                    end += self.scanner_position.__getattribute__(axis_name)
                self._data.end.__setattr__(axis_name, end)
            elif row == RowNumber.step_split:
                start = self._data.start.__getattribute__(axis_name)
                end = self._data.end.__getattribute__(axis_name)
                if self.split_type == "step":
                    self._data.step.__setattr__(axis_name, float(value))
                    self._data.points.__setattr__(axis_name, math.floor(abs(end - start) / float(value)))
                elif self.split_type == "points":
                    self._data.points.__setattr__(axis_name, int(value))
                    self._data.step.__setattr__(axis_name, (abs(end - start) / int(value)))
            elif row == RowNumber.order:
                self._data.order.__setattr__(axis_name, int(value))
            elif row == RowNumber.enable_disable_status:
                self._data.enable_disable_status.__setattr__(axis_name, int(value))

            self.dataChanged.emit(index, index)
            self.signals.data_changed.emit()
        return True


class TablePathModel(PPath):
    type_name = 'Table'
    base_name = 'path'

    def __init__(self, name: str, scanner: PScanner):
        super(TablePathModel, self).__init__(name=name)
        self.table_model = TableModel(scanner)
        self.scanner = scanner
        self.trajectory_type = "Snake"

        self.table_model.signals.data_changed.connect(self.signals.display_changed.emit)

    @classmethod
    def reproduce(cls, name: str, project: ProjectType) -> 'TablePathModel':
        return cls(scanner=project.scanner, name=name)

    def set_relative(self, state: bool):
        self.table_model.set_relative(state)

    def set_split_type(self, split_type: str):
        self.table_model.set_split_type(split_type)

    def set_current_coords(self):
        self.table_model.match_positions()

    def get_points_axes(self) -> tuple[str, ...]:
        return 'x', 'y', 'z', 'w'

    def get_points_ndarray(self) -> np.ndarray:

        """связать с функцией mesh_maker"""
        return self.get_path()

    def get_points(self) -> list[Position]:
        """
        Возвращает массив точек, в которых необходимо провести измерения.
        """
        res = []
        points = self.get_points_ndarray()
        for point in points:
            position = Position(
                **{name: value for name, value in zip(self.get_points_axes(), point)}
            )
            res.append(position)
        return res

    def set_trajectory_type(self, traj_type: str):
        self.trajectory_type = traj_type
        self.signals.display_changed.emit()

    def mesh_maker(self, axes: list[np.ndarray], order: Union[None, list[int]] = None):
        """
        функция осуществляет измерения с заданым разбиением по траектории змейка или линия
        :param axes:
        :return:
        """
        if order is None:
            order = [0, 1, 2, 3]
        axes_ordered = axes.copy()
        if set(order) != {0, 1, 2, 3}:
            raise ValueError(f'order collision is prohibited')

        for i, j in enumerate(order):
            if j < 0 or j > 3:
                raise ValueError(f'order must be in range(0, 4) {j} got')
            axes[j] = axes_ordered[i]

        blck_sizes = [len(ax) for ax in axes]
        crds = np.zeros((len(axes), np.prod(blck_sizes)), dtype=np.float32)
        crds[-1] = np.repeat(axes[-1], np.prod(blck_sizes[:-1]))

        for i in range(len(axes) - 1):
            rep_num = np.prod(blck_sizes[:i])
            rep_el = np.repeat(axes[i], rep_num)
            tile_num = np.prod(blck_sizes[i + 1:])
            if self.trajectory_type == 'Snake':
                tile_el = np.concatenate((rep_el, np.flip(rep_el)))
            elif self.trajectory_type == 'Lines':
                tile_el = np.concatenate((rep_el, rep_el))
            if tile_num % 2 != 0:
                crds[i] = np.concatenate((np.tile(tile_el, tile_num // 2), rep_el))
            else:
                crds[i] = np.tile(tile_el, tile_num // 2)

        crds_ordered = np.empty(crds.shape, dtype=np.float32)
        for i, j in enumerate(order):
            crds_ordered[i] = crds[j]

        return crds_ordered.T

    def get_path(self):
        """
        берет данные из таблицы и выдает путь в соответствии с заданными параметрами (змейка или линия и тд)
        :return:
        """
        temp = []
        order = []
        role = Qt.ItemDataRole.DisplayRole

        for axis in ['x', 'y', 'z', 'w']:
            start = self.table_model._data.start.__getattribute__(axis)
            stop = self.table_model._data.end.__getattribute__(axis)
            status = self.table_model._data.enable_disable_status.__getattribute__(axis)

            if status == 1:
                points_numbers = self.table_model._data.points.__getattribute__(axis)
            elif status == 0:
                points_numbers = 1
            else:
                raise ValueError(f'0 or 1 acceptable got {status}')

            order.append(self.table_model._data.order.__getattribute__(axis))
            current_data = np.linspace(float(start), float(stop), points_numbers)
            temp.append(current_data)
        return self.mesh_maker(temp, order)


