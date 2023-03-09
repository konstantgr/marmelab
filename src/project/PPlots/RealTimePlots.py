import numpy as np

from .. import PMeasurand
from ..Project import PRealTimePlot, PPlot1D, PPlot2D, PPlot3D, ProjectType, PStorage, PBaseSignals
from typing import Union, Tuple, List, Type
from PyQt6.QtCore import pyqtBoundSignal, pyqtSignal


class TSignals(PBaseSignals):
    measurands_changed: pyqtBoundSignal = pyqtSignal()


class PRTPlot1D(PPlot1D, PRealTimePlot):
    signals_type = TSignals
    signals: TSignals

    def __init__(self, name: str, measurands: PStorage[PMeasurand]):
        super(PRTPlot1D, self).__init__(name=name)

        self.x = np.array([])
        self.f = np.array([])
        self.x_data_name = None
        self.f_data_name = None
        self._auto_update = True
        self._auto_update_time_delay = 0.1
        self._measurand = None
        self._measurands = measurands

        self._measurands.signals.changed.connect(self.measurands_updated)

    def measurands_updated(self):
        self.signals.measurands_changed.emit()

    def update(self):
        # if isinstance(self._measurand, PMeasurand):
        #     self._measurand.measure()
        self.x = np.linspace(0, 10, 100)
        self.f = np.sin(self.x) + np.random.normal(0, 0.2, 100)

    def get_x(self) -> np.ndarray:
        print(self.x)
        return self.x

    def get_f(self) -> np.ndarray:
        return self.f

    # @property
    # def auto_update(self) -> bool:
    #     return self._auto_update
    #
    # @property
    # def auto_update_time_delay(self) -> float:
    #     return self._auto_update_time_delay

    @property
    def measurand(self) -> Union[PMeasurand, None]:
        return self._measurand

    def get_measurands(self) -> List[PMeasurand]:
        return self._measurands.data

    def set_measurand(self, measurand: PMeasurand):
        self._measurand = measurand
        self.x = np.array([])
        self.f = np.array([])
        self.x_data_name = None
        self.f_data_name = None
        self.signals.display_changed.emit()

    def set_x_data_name(self, name: str):
        self.x_data_name = name

    def set_f_data_name(self, name: str):
        self.f_data_name = name
    # def set_auto_update(self, state: bool):
    #     self._auto_update = state
    #
    # def set_auto_update_time_delay(self, time: float):
    #     self._auto_update_time_delay = time

    @classmethod
    def reproduce(cls, name: str, project: ProjectType) -> 'PRTPlot1D':
        return cls(name=name, measurands=project.measurands)

