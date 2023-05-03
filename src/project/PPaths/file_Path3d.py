from ..Project import PPath, ProjectType
from PyQt6.QtCore import pyqtBoundSignal, pyqtSignal, QObject
from typing import Union, Tuple
import numpy as np
from src.views.Widgets.SettingsTable import QAbstractTableModel
from ..Project import PPath, PScanner
from PyQt6.QtCore import Qt, QObject, QModelIndex
from typing import Any
from ...scanner import Position
from dataclasses import dataclass, field
import math
from enum import IntEnum, auto
import time


class FilePathModel(PPath):
    type_name = 'File'
    base_name = 'path'

    def __init__(self, name: str):
        super(FilePathModel, self).__init__(name=name)
        self.path: np.array = np.array([[0, 0, 0, 0], [0, 0, 0, 0]])

    @classmethod
    def reproduce(cls, name: str, project: ProjectType) -> 'FilePathModel':
        return cls(name=name)

    def set_path(self, path):
        self.path = path
        self.signals.display_changed.emit()

    def get_points_ndarray(self) -> np.ndarray:
        return self.path

    def get_points_axes(self) -> Tuple[str, ...]:
        return 'x', 'y', 'z', 'w'

