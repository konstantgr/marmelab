import numpy as np

from ..scanner import Scanner, ScannerSignals
from ..analyzator import AnalyzerSignals, BaseAnalyzer
from ..scanner import BaseAxes, Position, Velocity, Acceleration, Deceleration
from PyQt6.QtCore import pyqtBoundSignal, pyqtSignal, QObject
from dataclasses import dataclass
from abc import abstractmethod, ABC, ABCMeta
from typing import Union, Generic, TypeVar, Tuple
from ..Variable import Setting


def _meta_resolve(cls):
    class _MetaResolver(type(QObject), type(cls)):
        # https://stackoverflow.com/questions/28720217/multiple-inheritance-metaclass-conflict
        pass
    return _MetaResolver


class PBaseSignals(QObject):
    """Сигналы PBase"""
    # TODO: remove changed ?
    changed: pyqtBoundSignal = pyqtSignal()
    name_changed: pyqtBoundSignal = pyqtSignal()
    display_changed: pyqtBoundSignal = pyqtSignal()


class PBase:
    """
    Базовый класс всех объектов в проекте
    """

    def __init__(
            self,
            name: str,
    ):
        self.name = name
        self.signals = PBaseSignals()


class PObject(PBase):
    """
    Класс объекта исследования
    """


class PPath(PBase, metaclass=ABCMeta):
    """
    Класс пути перемещения сканера
    """

    @abstractmethod
    def get_points_axes(self) -> Tuple[str, ...]:
        """
        Возвращает оси координат в том порядке, в котором они измеряются, например ("x", "z")
        """

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

    @abstractmethod
    def get_points_ndarray(self) -> np.ndarray:
        """
        Возвращает массив точек, в которых необходимо провести измерения.
        Размерность массива (n x m), где m - число координат, а n число измеряемых точек
        """


class PState(QObject):
    """
    Класс состояния.
    PState по своей сути является bool.
    У PState существует сигнал changed_signal, в который делается emit
    при изменении значения состояния на противоположное.

    Работают логические операции с состояниями, например is_connected & is_moving является PState,
    значение которого положительно, если оба PState положительны.
    При этом новый PState имеет changed_signal и сам отслеживает изменения каждого из состояний
    в произведении.
    """
    changed_signal: pyqtBoundSignal = pyqtSignal()

    def __init__(self, value: bool, signal: pyqtBoundSignal = None):
        """

        :param value: начальное значение
        :param signal: сигнал pyqtSignal[bool], от которого зависит значение состояния.
        Если в сигнал было заэмичено новое значение, то состояние будет обновлено.
        """
        super(PState, self).__init__()
        self._value = value
        if signal is not None:
            signal.connect(self.set)

    def set(self, state: bool):
        """
        Выставить новое значение состояния
        """
        if self._value != state:
            self._value = state
            self.changed_signal.emit()

    def __bool__(self) -> bool:
        return self._value

    def __and__(self, other):
        new_state = PState(value=bool(self) and bool(other))

        def update():
            """Вспомогательный апдейтер"""
            state = bool(self) and bool(other)
            new_state.set(state)

        self.changed_signal.connect(update)
        other.changed_signal.connect(update)
        return new_state

    def __or__(self, other):
        new_state = PState(value=bool(self) and bool(other))

        def update():
            """Вспомогательный апдейтер"""
            state = bool(self) or bool(other)
            new_state.set(state)

        self.changed_signal.connect(update)
        other.changed_signal.connect(update)
        return new_state

    def __invert__(self):
        new_state = PState(value=not bool(self))

        def update():
            """Вспомогательный апдейтер"""
            state = not bool(self)
            new_state.set(state)

        self.changed_signal.connect(update)
        return new_state


class PScannerSignals(QObject, ScannerSignals, metaclass=_meta_resolve(ScannerSignals)):
    """
    Сигналы сканера, возможно, некоторые из них бесполезны
    """
    position: pyqtBoundSignal = pyqtSignal([BaseAxes], [Position])
    velocity: pyqtBoundSignal = pyqtSignal([BaseAxes], [Velocity])
    acceleration: pyqtBoundSignal = pyqtSignal([BaseAxes], [Acceleration])
    deceleration: pyqtBoundSignal = pyqtSignal([BaseAxes], [Deceleration])
    is_connected: pyqtBoundSignal = pyqtSignal(bool)
    is_moving: pyqtBoundSignal = pyqtSignal(bool)


@dataclass
class PScannerStates:
    """
    Все возможные состояния сканера
    """
    is_connected: PState  # подключен
    is_moving: PState  # в движении
    is_in_use: PState  # используется ли в эксперименте прямо сейчас


ScannerType = TypeVar('ScannerType', bound=Scanner)


class PScanner(ABC):
    """
    Класс сканера, объединяющего сам сканер, его состояния и сигналы
    """
    def __init__(
            self,
            instrument: ScannerType,
            signals: PScannerSignals,
    ):
        self.signals = signals
        self.instrument = instrument
        self.states = PScannerStates(
            is_connected=PState(False, self.signals.is_connected),
            is_moving=PState(False, self.signals.is_moving),
            is_in_use=PState(False),
        )

    @property
    @abstractmethod
    def dims_number(self) -> int:
        """

        :return: Возвращает размерность рабочего пространства
        """

    @property
    @abstractmethod
    def axes_number(self) -> int:
        """

        :return: Возвращает количество осей
        """

    @abstractmethod
    def get_settings(self) -> list[Setting]:
        """
        Возвращает настройки, которые можно изменить
        :return:
        """


class PScannerVisualizer(ABC):
    """
    Класс визуализатора сканера
    """
    def __init__(
            self,
            scanner: PScanner
    ):
        self.scanner = scanner


class PMeasurandSignals(QObject):
    changed: pyqtBoundSignal = pyqtSignal()
    measured: pyqtBoundSignal = pyqtSignal()


class PMeasurand(ABC):
    """
    Физическая величина, которая может быть измерена анализатором
    """
    def __init__(
            self,
            name: str,
    ):
        """

        :param name: название, например S-parameters, Signal amplitude
        """
        self.name = name
        self.signals = PMeasurandSignals()

    @abstractmethod
    def measure(self) -> np.ndarray:
        """
        Провести измерение величины и сохранить значения
        """

    @abstractmethod
    def pre_measure(self) -> None:
        """
        Настроить анализатор перед измерением данной величины
        """

    @abstractmethod
    def get_measure_names(self) -> Tuple[str, ...]:
        """
        Возвращает кортеж названий измеренных величин, например (“freq”, “S11”)
        """

    @abstractmethod
    def get_data(self) -> Union[None, np.ndarray]:
        """
        Вернуть предыдущие значение. None, если измерений еще не было
        """


class PAnalyzerSignals(QObject, AnalyzerSignals, metaclass=_meta_resolve(AnalyzerSignals)):
    """
    Сигналы анализатора
    """
    connect: pyqtBoundSignal = pyqtSignal()
    disconnect: pyqtBoundSignal = pyqtSignal()
    set_settings: pyqtBoundSignal = pyqtSignal(dict)
    data: pyqtBoundSignal = pyqtSignal(dict)
    is_connected: pyqtBoundSignal = pyqtSignal(bool)


@dataclass
class PAnalyzerStates:
    """
    Все возможные состояния сканера
    """
    is_connected: PState
    is_in_use: PState  # используется в эксперименте прямо сейчас


AnalyzerType = TypeVar('AnalyzerType', bound=BaseAnalyzer)


class PAnalyzer(ABC):
    """
    Класс анализатора, объединяющий сигналы и статусы анализатора.
    """
    def __init__(
            self,
            signals: PAnalyzerSignals,
            instrument: AnalyzerType,
    ):
        self.signals = signals
        self.instrument = instrument
        self.states = PAnalyzerStates(
            is_connected=PState(False, self.signals.is_connected),
            is_in_use=PState(False),
        )
        self.current_measurand: Union[PMeasurand, None] = None  # измерение, к которому подготовлен анализатор

        self.signals.connect.connect(self.instrument.connect)
        self.signals.disconnect.connect(self.instrument.disconnect)
        self.signals.set_settings.connect(self._set_settings)

    def _set_settings(self, d: dict):
        self.current_measurand = None
        self.instrument.set_settings(**d)

    def set_current_measurand(self, measurand: PMeasurand):
        """Объявить measurand, к которому подготовлен анализатор"""
        self.current_measurand = measurand

    @abstractmethod
    def get_measurands(self) -> list[PMeasurand]:
        """
        Вернуть лист величин, которые можно измерить
        """


class PResults(PBase):
    """
    Класс результатов
    """
    @abstractmethod
    def get_data(self) -> np.ndarray:
        """
        Возвращает все сохраненные данные
        """

    @abstractmethod
    def get_data_names(self) -> Tuple[str, ...]:
        """
        Возвращает названия колонок данных
        """

    @abstractmethod
    def append_data(self, data: np.ndarray):
        """
        Добавить новую строку в результаты
        """


class PExperiment(PBase):
    """
    Класс эксперимента
    """
    @abstractmethod
    def run(self):
        """
        Запуск эксперимента
        """


class PPlot1D(PBase):
    """
    """
    @abstractmethod
    def get_x(self) -> np.ndarray:
        """
        :return: возвращает х
        """

    @abstractmethod
    def get_f(self) -> np.ndarray:
        """
        :return: возвращает значение функции f(х)
        """


class PPlot2D(PPlot1D, ABC):
    """
    Класс графиков
    """
    @abstractmethod
    def get_y(self) -> np.ndarray:
        """
        :return: возвращает у
        """


class PPlot3D(PPlot2D):
    """
    Класс графиков
    """
    @abstractmethod
    def get_z(self) -> np.ndarray:
        """
        :return: возвращает z
        """


class PStorageSignals(QObject):
    """
    Сигналы хранилища
    """
    changed: pyqtBoundSignal = pyqtSignal()  # эмит при .add() и .delete()
    add: pyqtBoundSignal = pyqtSignal(PBase)
    delete: pyqtBoundSignal = pyqtSignal(PBase)


PBaseTypes = TypeVar('PBaseTypes', PBase, PExperiment, PResults, PMeasurand, PObject, PPath, PPlot1D, PPlot2D, PPlot3D)


class PStorage(Generic[PBaseTypes]):
    """
    Базовое хранилище объектов проекта
    """
    def __init__(
            self,
            last_index: int = 0,
    ):
        self.signals = PStorageSignals()
        self.data: list[PBaseTypes] = []
        self.signals.add.connect(self.append)
        self.signals.delete.connect(self.delete)
        self.last_index = last_index  # каждый append увеличивает last_index на 1

    def append(self, x: PBaseTypes):
        """
        Добавить элемент в хранилище
        """
        self.data.append(x)
        self.last_index += 1
        self.signals.changed.emit()

    def delete(self, x: PBaseTypes):
        """
        Удалить элемент из хранилища
        """
        x.signals.changed.disconnect()
        self.data.remove(x)
        self.signals.changed.emit()


class PAnalyzerVisualizer(ABC):
    """
    Класс визуализатора анализатора
    """
    def __init__(
            self,
            plots_1d: PStorage[PPlot1D],
            plots_2d: PStorage[PPlot2D],
            plots_3d: PStorage[PPlot3D],
    ):
        self.plots_1d = plots_1d
        self.plots_2d = plots_2d
        self.plots_3d = plots_3d


PScannerTypes = TypeVar('PScannerType', bound=PScanner)
PAnalyzerTypes = TypeVar('PAnalyzerTypes', bound=PAnalyzer)

class Project:
    """
    Класс всего проекта
    """
    def __init__(
            self,
            scanner: PScannerTypes,
            analyzer: PAnalyzerTypes,
            scanner_visualizer: PScannerVisualizer,
            analyzer_visualizer: PAnalyzerVisualizer,
            objects: PStorage[PObject],
            paths: PStorage[PPath],
            measurands: PStorage[PMeasurand],
            experiments: PStorage[PExperiment],
            results: PStorage[PResults],
            plots_1d: PStorage[PPlot1D],
            plots_2d: PStorage[PPlot2D],
            plots_3d: PStorage[PPlot3D],
    ):
        self.scanner = scanner
        self.analyzer = analyzer
        self.scanner_visualizer = scanner_visualizer
        self.analyzer_visualizer = analyzer_visualizer

        self.objects = objects
        self.paths = paths
        self.measurands = measurands
        self.experiments = experiments
        self.results = results

        self.plots_1d = plots_1d
        self.plots_2d = plots_2d
        self.plots_3d = plots_3d
