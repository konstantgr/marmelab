from ..Project import PWidget, PPath
from PyQt6.QtWidgets import QTextEdit
import numpy as np


class Settings(QTextEdit):
    def __init__(self):
        super(Settings, self).__init__('')
        self.setText('Path Settings')


class Path3d(PPath):
    def __init__(
            self,
            name: str,
            points: np.ndarray
    ):
        super(Path3d, self).__init__(
            widget=PWidget(
                name,
                Settings()
            )
        )

        self.points = points



