import numpy as np

from .. import PMeasurand
from ..Project import PRealTimePlot, PPlot1D, PPlot2D, PPlot3D, ProjectType, PStorage, PBaseSignals
from typing import Union, Tuple, List, Type, Callable
from PyQt6.QtCore import pyqtBoundSignal, pyqtSignal, pyqtSlot, QObject


class ResPPlot3DS(PPlot2D):
    def __init__(self, name, results: PStorage):
        super(ResPPlot3DS, self).__init__(name=name)
        self.results = results

    def update(self):
        self.signals.display_changed.emit()

    def get_y(self) -> np.ndarray:
        pass

    def get_x(self) -> np.ndarray:
        pass

    def get_f(self) -> np.ndarray:
        pass

    def get_results(self) -> dict[str: list[str]]:
        res = {}
        for result in self.results.data:
            res[result.name] = list(result.get_data_names())
        return res

    @classmethod
    def reproduce(cls, name: str, project: ProjectType) -> 'ResPPlot3DS':
        return cls(name=name, results=project.results)
