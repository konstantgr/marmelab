import numpy as np

from .. import PMeasurand
from ..Project import PRealTimePlot, PPlot1D, PPlot2D, PPlot3D, ProjectType, PStorage, PBaseSignals
from typing import Union, Tuple, List, Type, Callable
from PyQt6.QtCore import pyqtBoundSignal, pyqtSignal, pyqtSlot, QObject


class TSignals(PBaseSignals):
    measurands_changed: pyqtBoundSignal = pyqtSignal()
    current_measurand_measured: pyqtBoundSignal = pyqtSignal()
    _current_measurand_changed: pyqtBoundSignal = pyqtSignal()
    current_measurand_changed: pyqtBoundSignal = pyqtSignal()


class Wrapper(QObject):
    """
    Штука, чтобы работал disconnect и connect
    """
    def __init__(self, func: Callable, *args, **kwargs):
        super(Wrapper, self).__init__(*args, **kwargs)
        self.func = func

    @pyqtSlot()
    def call(self):
        self.func()


class PRTPlot1D(PPlot1D, PRealTimePlot):
    signals_type = TSignals
    signals: TSignals

    def __init__(self, name: str, measurands: PStorage[PMeasurand]):
        super(PRTPlot1D, self).__init__(name=name)

        self.x_data_name = ''
        self.f_data_name = ''
        self.current_measurand_name = ''
        self.measurands_storage = measurands

        self.measurands_storage.signals.changed.connect(self._measurands_updated)
        self.signals._current_measurand_changed.connect(self._measurand_changed)

    def _clear(self):
        self.x_data_name = ''
        self.f_data_name = ''

    def _measurands_updated(self):
        if self.current_measurand_name not in self.measurands_storage:
            self._clear()
            self.current_measurand_name = ''
        self.signals.measurands_changed.emit()

    def _measurand_changed(self):
        names = self.measurand.get_measure_names()
        if self.x_data_name not in names:
            self.x_data_name = ''
        if self.f_data_name not in names:
            self.f_data_name = ''
        self.signals.current_measurand_changed.emit()

    def update(self):
        current_measurand = self.measurand
        if current_measurand is None:
            raise Exception(f"Measurand is not selected")
        current_measurand.measure()
        self.signals.current_measurand_measured.emit()

    def get_x(self) -> np.ndarray:
        measurand = self.measurand
        res = measurand.get_data()
        if res is None:
            return np.array([])
        names = measurand.get_measure_names()
        ind = names.index(self.x_data_name)
        return res[ind]

    def get_f(self) -> np.ndarray:
        measurand = self.measurand
        res = measurand.get_data()
        if res is None:
            return np.array([])
        names = measurand.get_measure_names()
        ind = names.index(self.f_data_name)
        return res[ind]

    @property
    def measurand(self) -> Union[PMeasurand, None]:
        return self.measurands_storage.get(self.current_measurand_name)

    def get_measurands(self) -> dict[str: list[str]]:
        """
        Возвращает межеранды и их измеряемые величины

        :return:
        """
        res = {}
        for measurand in self.measurands_storage.data:
            res[measurand.name] = list(measurand.get_measure_names())
        return res

    def set_settings(self, measurand_name: str, x_data_name: str, f_data_name: str):

        new_measurand = self.measurands_storage.get(measurand_name)
        if new_measurand is None:
            raise Exception(f"Can't find measurand {measurand_name}")

        if not(self.current_measurand_name == measurand_name):
            if self.measurand is not None:
                self.measurand.signals.measured.disconnect(self.signals.current_measurand_measured)
                self.measurand.signals.changed.disconnect(self.signals._current_measurand_changed)
            new_measurand.signals.measured.connect(self.signals.current_measurand_measured)
            new_measurand.signals.changed.connect(self.signals._current_measurand_changed)
            self.current_measurand_name = measurand_name
            self._clear()

        self._set_x_data_name(x_data_name)
        self._set_f_data_name(f_data_name)

        print(x_data_name, f_data_name)
        self.signals.changed.emit()

    def _check_data_name(self, name: str):
        if self.measurand is None:
            raise Exception(f"Measurand is not selected")
        available_names = self.measurand.get_measure_names()
        if name not in available_names:
            raise Exception(f"Wrong measure name {name}, available names: {available_names}")

    def _set_x_data_name(self, name: str):
        self._check_data_name(name)
        self.x_data_name = name

    def _set_f_data_name(self, name: str):
        self._check_data_name(name)
        self.f_data_name = name

    @classmethod
    def reproduce(cls, name: str, project: ProjectType) -> 'PRTPlot1D':
        return cls(name=name, measurands=project.measurands)

