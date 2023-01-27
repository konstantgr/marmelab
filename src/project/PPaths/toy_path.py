from ..Project import PPath
import numpy as np


class ToyPath(PPath):
    def __init__(self, name: str):
        super(ToyPath, self).__init__(name=name)
        self.x_min = 0
        self.y_min = 0
        self.x_max = 0
        self.y_max = 0

    def set_lims(self, x_min, x_max, y_min, y_max):
        self.x_min = x_min
        self.y_min = y_min
        self.x_max = x_max
        self.y_max = y_max

    def get_points_axes(self) -> tuple[str, ...]:
        return "y", "x"

    def get_points_ndarray(self) -> np.ndarray:
        res = []
        xs = np.linspace(self.x_min, self.x_max, 1000)
        ys = np.linspace(self.x_min, self.x_max, 1000)

        for i in range(len(xs)):
            for j in range(len(ys)):
                if i % 2 == 0:
                    res.append([xs[i], ys[j]])
                else:
                    res.append([xs[i], ys[-j-1]])
        return np.ndarray(res)
