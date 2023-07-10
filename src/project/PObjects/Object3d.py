from ..Project import PObject, PWidget
from PyQt6.QtWidgets import QTextEdit, QWidget
import os
from stl import mesh
import numpy as np


class Settings(QTextEdit):
    def __init__(self):
        super(Settings, self).__init__('')
        self.setText('Object Settings')


class Object3d(PObject):
    def __init__(
            self,
            name: str,
    ):
        super(Object3d, self).__init__(
            name=name,
            widget=Settings()
        )
        filename = os.path.join(os.path.dirname(__file__), 'assets/cylinder.stl')
        self.mesh = mesh.Mesh.from_file(filename)

        self._x = 1000
        self._y = 500
        self._z = 3000
        self._h = 1000
        self._r = 250

    @property
    def transformation(self) -> np.ndarray:
        res = np.eye(4)
        res[0, 0] = res[1, 1] = self._r * 2
        res[2, 2] = self._h
        res[0, 3] = self._z
        res[1, 3] = self._x
        res[2, 3] = self._y
        return res



