import numpy as np

from ..scanner import Scanner, ScannerSignals
from ..analyzers import AnalyzerSignals, BaseAnalyzer
from ..scanner import BaseAxes, Position, Velocity, Acceleration, Deceleration
from PyQt6.QtCore import pyqtBoundSignal, pyqtSignal, QObject
from PyQt6.QtWidgets import QWidget
from dataclasses import dataclass
from abc import abstractmethod, ABC, ABCMeta
from typing import Union, Generic, TypeVar, Tuple, Type
from ..Variable import Setting


def _meta_resolve(cls):
    class _MetaResolver(type(QObject), type(cls)):
        # https://stackoverflow.com/questions/28720217/multiple-inheritance-metaclass-conflict
        pass
    return _MetaResolver


class PNamed:
    """Класс с названиями"""
    base_name = 'noname'
    type_name = 'No name'

    def __init__(
            self,
            name: str,
    ):
        self.name = name


class PBaseSignals(QObject):
    """Сигналы PBase"""
    # TODO: remove changed ?
    changed: pyqtBoundSignal = pyqtSignal()
    name_changed: pyqtBoundSignal = pyqtSignal()
    display_changed: pyqtBoundSignal = pyqtSignal()
    data_changed: pyqtBoundSignal = pyqtSignal()


SignalsTypes = TypeVar('SignalsTypes')
ProjectType = TypeVar('ProjectType', bound='Project')


class PBase(PNamed, Generic[SignalsTypes], metaclass=ABCMeta):
    """
    Базовый класс всех объектов в проекте
    """
    base_name = 'base'
    type_name = 'Base'
    signals_type: Type[SignalsTypes] = PBaseSignals

    def __init__(
            self,
            name: str,
    ):
        super(PBase, self).__init__(name=name)
        self.signals: SignalsTypes = self.signals_type()

    # def __init_subclass__(cls, **kwargs):
    #     # cls.signals_type = PBaseSignals
    #     print(cls.signals_type)

    @classmethod
    @abstractmethod
    def reproduce(cls, name: str, project: ProjectType) -> 'PBaseTypes':
        """Создает экземпляр класса"""


class PObject(PBase, metaclass=ABCMeta):
    """
    Класс объекта исследования
    """
    base_name = 'obj'
    type_name = 'Object'


class PPath(PBase, metaclass=ABCMeta):
    """
    Класс пути перемещения сканера
    """
    base_name = 'path'
    type_name = 'Path'

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


class PScanner(PNamed, metaclass=ABCMeta):
    """
    Класс сканера, объединяющего сам сканер, его состояния и сигналы
    """
    base_name = 'sc'
    type_name = 'Scanner'

    def __init__(
            self,
            name: str,
            instrument: ScannerType,
            signals: PScannerSignals,
    ):
        super(PScanner, self).__init__(name=name)
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


class PScannerVisualizer(PNamed, metaclass=ABCMeta):
    """
    Класс визуализатора сканера
    """


class PMeasurandSignals(QObject):
    """Сигналы межеранда"""
    changed: pyqtBoundSignal = pyqtSignal()
    measured: pyqtBoundSignal = pyqtSignal()


class PMeasurand(PBase, metaclass=ABCMeta):
    """
    Физическая величина, которая может быть измерена анализатором
    """
    base_name = 'meas'
    type_name = 'Measurand'

    def __init__(
            self,
            name: str,
    ):
        super(PMeasurand, self).__init__(name=name)
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
    def get_measure_names(self) -> Tuple[str]:
        """
        Возвращает кортеж названий измеренных величин, например (“freq”, “S11”)
        """

    @abstractmethod
    def get_data(self) -> Union[None, np.ndarray]:
        """
        Вернуть предыдущие значение. None, если измерений еще не было
        """


PMeasurandType = TypeVar('PMeasurandType', bound=PMeasurand)


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


class PAnalyzer(PNamed, metaclass=ABCMeta):
    """
    Класс анализатора, объединяющий сигналы и статусы анализатора.
    """
    base_name = 'an'
    type_name = 'Analyzer'

    def __init__(
            self,
            name: str,
            signals: PAnalyzerSignals,
            instrument: AnalyzerType,
    ):
        super(PAnalyzer, self).__init__(name=name)
        self.signals = signals
        self.instrument = instrument
        self.states = PAnalyzerStates(
            is_connected=PState(False, self.signals.is_connected),
            is_in_use=PState(False),
        )
        self.current_measurand: Union[PMeasurand, None] = None  # измерение, к которому подготовлен анализатор

        self.signals.connect.connect(self.instrument.connect)
        self.signals.disconnect.connect(self.instrument.disconnect)
        self.signals.set_settings.connect(self.set_settings)

    def set_settings(
            self,
            measurand: Union[PMeasurand, None] = None,
            **settings
    ):
        self.instrument.set_settings(settings)
        self.set_current_measurand(measurand)

    def set_current_measurand(self, measurand: PMeasurand):
        """Объявить measurand, к которому подготовлен анализатор"""
        self.current_measurand = measurand

    @staticmethod
    @abstractmethod
    def get_measurands(self) -> list[Type[PMeasurand]]:
        """
        Вернуть лист величин, которые можно измерить
        """


class PResults(PBase):
    """
    Класс результатов
    """
    base_name = 'res'
    type_name = 'Results'

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
    base_name = 'exp'
    type_name = 'Experiment'

    @abstractmethod
    def run(self):
        """
        Запуск эксперимента
        """


class PRealTimePlot(metaclass=ABCMeta):
    """График, который обновляется по времени"""

    # @property
    # @abstractmethod
    # def auto_update(self) -> bool:
    #     """Обновлять ли график автоматически"""
    #
    # @property
    # @abstractmethod
    # def auto_update_time_delay(self) -> float:
    #     """Задержка между запросами на обновление"""

    @property
    @abstractmethod
    def measurand(self) -> PMeasurand:
        """Measurand для которого строится график"""


class PResultsPlot(metaclass=ABCMeta):
    """График, который обновляется, когда в PResults появились новые данные"""
    # @property
    # @abstractmethod
    # def auto_update(self) -> bool:
    #     """Обновлять ли график автоматически"""

    @property
    @abstractmethod
    def results(self) -> PResults:
        """Results для которого строится график"""


class PPlot1D(PBase):
    """Класс графиков f(x)"""
    base_name = 'plt'
    type_name = 'Plot f(x)'

    @abstractmethod
    def update(self):
        """Обновить data"""

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


class PPlot2D(PPlot1D, metaclass=ABCMeta):
    """
    Класс графиков f(x, y)
    """
    type_name = 'Plot f(x, y)'

    @abstractmethod
    def get_y(self) -> np.ndarray:
        """
        :return: возвращает у
        """


class PPlot3D(PPlot2D, metaclass=ABCMeta):
    """
    Класс графиков f(x, y, z)
    """
    type_name = 'Plot f(x, y, z)'

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


PBaseTypes = TypeVar('PBaseTypes', PBase, PExperiment, PResults, PMeasurand, PObject, PPath, PPlot1D, PPlot2D, PPlot3D)
PPlotTypes = TypeVar('PPlotTypes', PPlot1D, PPlot2D, PPlot3D)


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
        # TODO: добавить автоматический поиск всех сигналов в классе.
        if x.signals.receivers(x.signals.changed):
            x.signals.changed.disconnect()
        self.data.remove(x)
        self.signals.changed.emit()


class PAnalyzerVisualizer(PNamed, metaclass=ABCMeta):
    """
    Класс визуализатора анализатора
    """
    def __init__(
            self,
            name: str,
            plots: PStorage[PPlotTypes],
    ):
        super(PAnalyzerVisualizer, self).__init__(name=name)
        self.plots = plots


PScannerTypes = TypeVar('PScannerTypes', bound=PScanner)
PAnalyzerTypes = TypeVar('PAnalyzerTypes', bound=PAnalyzer)


class Project:
    """
    Класс всего проекта
    """
    def __init__(
            self,
            scanner: PScannerTypes,
            analyzer: PAnalyzerTypes,
            objects: PStorage[PObject],
            paths: PStorage[PPath],
            measurands: PStorage[PMeasurand],
            experiments: PStorage[PExperiment],
            results: PStorage[PResults],
            plots: PStorage[PPlotTypes],
            scanner_visualizer: PScannerVisualizer,
    ):
        self.scanner = scanner
        self.analyzer = analyzer

        self.objects = objects
        self.paths = paths
        self.measurands = measurands
        self.experiments = experiments
        self.results = results

        self.plots = plots

        self.scanner_visualizer = scanner_visualizer

    def get_storage_by_class(self, cls: Type) -> PStorage:
        """Return storage for class"""
        if issubclass(cls, PObject):
            return self.objects
        elif issubclass(cls, PPath):
            return self.paths
        elif issubclass(cls, PMeasurand):
            return self.measurands
        elif issubclass(cls, PExperiment):
            return self.experiments
        elif issubclass(cls, PResults):
            return self.results
        elif issubclass(cls, (PPlot1D, PPlot2D, PPlot3D)):
            return self.plots
        else:
            raise TypeError(f"Can't find storage for {cls} class")

    def get_storages(self) -> Tuple[PStorage, ...]:
        return self.objects, self.paths, self.measurands,\
               self.experiments, self.results, self.plots


