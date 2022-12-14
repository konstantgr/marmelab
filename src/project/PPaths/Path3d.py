from ..Project import PWidget, PPath
from PyQt6.QtWidgets import QTextEdit, QWidget
import numpy as np
from dataclasses import dataclass, field


class Settings(QTextEdit):
    def __init__(self):
        super(Settings, self).__init__('')
        self.setText('Path Settings 123 ')


@dataclass
class Path3d(PPath):
    widget: QWidget = field(default_factory=Settings)
    points: np.ndarray = field(default_factory=np.ndarray)
