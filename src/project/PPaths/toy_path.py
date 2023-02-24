from ..Project import PPath, ProjectType
import numpy as np
from src.views.Widgets.SettingsTable import QAbstractTableModel


class ToyPath(PPath):
    def __init__(self, name: str):
        super(ToyPath, self).__init__(name=name)
        self.x_min = None
        self.y_min = None
        self.p = None
        self.y_max = None
        self.x_points = None
        self.y_points = None

    @classmethod
    def reproduce(cls, name: str, project: ProjectType) -> 'ToyPath':
        return cls(name=name)

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


