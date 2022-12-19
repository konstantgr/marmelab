from ..scanner import Scanner, ScannerSignals
from ..analyzator import AnalyzerSignals, BaseAnalyzer
from ..scanner import BaseAxes, Position, Velocity, Acceleration, Deceleration
from PyQt6.QtCore import pyqtBoundSignal, pyqtSignal, QObject
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QIcon
from dataclasses import dataclass, field
from abc import abstractmethod, ABC
from typing import Union, Callable, Generic, TypeVar, Any
from .icons import path_icon, object_icon, base_icon
from pyqtgraph import PlotWidget, GraphicsLayoutWidget


def _meta_resolve(cls):
    class _MetaResolver(type(QObject), type(cls)):
        # https://stackoverflow.com/questions/28720217/multiple-inheritance-metaclass-conflict
        pass
    return _MetaResolver


@dataclass
class PWidget:
    """
    Класс виджетов управления
    """
    name: str  # название виджета, например Settings, Control
    widget: QWidget
    icon: QIcon = None


class PBaseSignals(QObject):
    changed: pyqtBoundSignal = pyqtSignal()


@dataclass
class PBase:
    """
    Базовый класс всех объектов в проекте
    """
    name: str
    widget: QWidget
    icon: QIcon = base_icon
    signals: PBaseSignals = field(default_factory=PBaseSignals)


@dataclass
class PObject(PBase):
    """
    Класс объекта исследования
    """
    icon: QIcon = object_icon


@dataclass
class PPath(PBase):
    """
    Класс пути перемещения сканера
    """
    icon: QIcon = path_icon


@dataclass
class PMeasurable(PBase):
    """
    Класс измеряемой величины
    """


@dataclass
class PExperiment(PBase):
    """
    Класс эксперимента
    """


class PState(QObject):
    """
    Класс состояния.
    PState хранит только bool.
    У PState существует сигнал changed_signal, в который делается emit
    при изменении значения состояния на противоположное.

    Работают логические операции с состояниями, например is_connected & is_moving является PState,
    значение которого положительно, если оба PState положительны.
    При этом новый PState имеет changed_signal и сам отслеживает изменения каждого из состояний
    в произведении.
    """
    changed_signal: pyqtBoundSignal = pyqtSignal()

    def __init__(self, value: bool, signal: pyqtBoundSignal = None):
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
            # print(state)
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
    set_settings: pyqtBoundSignal = pyqtSignal(dict)
    stop: pyqtBoundSignal = pyqtSignal()
    abort: pyqtBoundSignal = pyqtSignal()
    connect: pyqtBoundSignal = pyqtSignal()
    disconnect: pyqtBoundSignal = pyqtSignal()
    home: pyqtBoundSignal = pyqtSignal()


@dataclass
class PScannerStates:
    """
    Все возможные состояния сканера
    """
    is_connected: PState  # подключен
    is_moving: PState  # в движении
    is_in_use: PState  # используется ли в эксперименте прямо сейчас


class PScanner(ABC):
    """
    Класс сканера, объединяющего состояния и сигналы
    """
    def __init__(
            self,
            instrument: Scanner,
            signals: PScannerSignals,
    ):
        self.signals = signals
        self.instrument = instrument
        self.states = PScannerStates(
            is_connected=PState(False, self.signals.is_connected),
            is_moving=PState(False, self.signals.is_moving),
            is_in_use=PState(False),
        )

        # соединяем сигналы для управления с функциями сканера
        self.signals.stop.connect(self.instrument.stop)
        self.signals.abort.connect(self.instrument.abort)
        self.signals.connect.connect(self.instrument.connect)
        self.signals.disconnect.connect(self.instrument.disconnect)
        self.signals.home.connect(self.instrument.home)
        self.signals.set_settings.connect(self._set_settings)

    def _set_settings(self, d: dict):
        self.instrument.set_settings(**d)

    @property
    @abstractmethod
    def control_widgets(self) -> list[PWidget]:
        """
        Виджеты, управляющие сканером
        """
        pass


class PScannerVisualizer(ABC):
    """
    Класс визуализатора сканера
    """
    def __init__(
            self,
            instrument: PScanner
    ):
        self.instrument = instrument

    @property
    @abstractmethod
    def widget(self) -> QWidget:
        """
        Виджет, отвечающий за визуализацию
        """
        pass

    @property
    @abstractmethod
    def control_widgets(self) -> list[PWidget]:
        """
        Виджеты, управляющие визуализацией
        """
        pass


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

    @property
    @abstractmethod
    def widget(self) -> QWidget:
        """
        Виджет измеряемой величины
        """

    @abstractmethod
    def measure(self) -> Any:
        """
        Провести измерение величины и перерисовать график, если такой есть
        """

    @abstractmethod
    def pre_measure(self) -> None:
        """
        Настроить сканер перед измерением данной величины
        """

    @property
    @abstractmethod
    def plot_widget(self) -> Union[PlotWidget, GraphicsLayoutWidget, None]:
        """
        PlotWidget этой величины
        """


class PAnalyzerSignals(QObject, AnalyzerSignals, metaclass=_meta_resolve(AnalyzerSignals)):
    """
    Сигналы анализатора
    """
    data: pyqtBoundSignal = pyqtSignal(dict)
    connect: pyqtBoundSignal = pyqtSignal()
    disconnect: pyqtBoundSignal = pyqtSignal()
    set_settings: pyqtBoundSignal = pyqtSignal(dict)
    is_connected: pyqtBoundSignal = pyqtSignal(bool)


@dataclass
class PAnalyzerStates:
    """
    Все возможные состояния сканера
    """
    is_connected: PState
    is_in_use: PState  # используется в эксперименте прямо сейчас


class PAnalyzer(ABC):
    """
    Класс анализатора, объединяющий сигналы и статусы анализатора
    """
    def __init__(
            self,
            signals: PAnalyzerSignals,
            instrument: BaseAnalyzer,
    ):
        self.signals = signals
        self.instrument = instrument
        self.states = PAnalyzerStates(
            is_connected=PState(False, self.signals.is_connected),
            is_in_use=PState(False),
        )

        self.signals.connect.connect(self.instrument.connect)
        self.signals.disconnect.connect(self.instrument.disconnect)
        self.signals.set_settings.connect(self._set_settings)

    def _set_settings(self, d: dict):
        self.instrument.set_settings(**d)

    @property
    @abstractmethod
    def control_widgets(self) -> list[PWidget]:
        """
        Виджеты, управляющие анализатором
        """

    @abstractmethod
    def get_measurands(self) -> list[PMeasurand]:
        """
        Вернуть лист величин, которые можно измерить
        """


class PStorageSignals(QObject):
    """
    Сигналы хранилища
    """
    changed: pyqtBoundSignal = pyqtSignal()  # эмит при .add() и .delete()
    element_changed: pyqtBoundSignal = pyqtSignal()  # эмит при сигнале PBase.sigmals.changed от любого элемента
    add: pyqtBoundSignal = pyqtSignal(PBase)
    delete: pyqtBoundSignal = pyqtSignal(PBase)


PBaseTypes = TypeVar('PBaseTypes', PBase, PExperiment, PMeasurable, PObject, PPath)


@dataclass
class PStorage(Generic[PBaseTypes]):
    """
    Базовое хранилище объектов проекта
    """
    signals: PStorageSignals = field(default_factory=PStorageSignals)
    data: list[PBaseTypes] = field(default_factory=list)

    def __post_init__(self):
        self.signals.add.connect(self.append)
        self.signals.delete.connect(self.delete)

    def append(self, x: PBaseTypes):
        """
        Добавить элемент в хранилище
        """
        self.data.append(x)
        x.signals.changed.connect(self._element_changed_emit)
        self.signals.changed.emit()

    def delete(self, x: PBaseTypes):
        """
        Удалить элемент из хранилища
        """
        x.signals.changed.disconnect()
        self.data.remove(x)
        self.signals.changed.emit()

    def _element_changed_emit(self):
        self.signals.element_changed.emit()


class PAnalyzerVisualizer(ABC):
    """
    Класс визуализатора анализатора
    """
    def __init__(
            self,
            measurables: PStorage[PMeasurable],
    ):
        self.measurables = measurables

    @property
    @abstractmethod
    def widget(self) -> QWidget:
        """
        Виджет визуализации
        """

    @property
    @abstractmethod
    def control_widgets(self) -> list[PWidget]:
        """
        Виджеты, управляющие визуализацией
        """


class Project:
    """
    Класс всего проекта
    """
    def __init__(
            self,
            scanner: PScanner,
            analyzer: PAnalyzer,
            scanner_visualizer: PScannerVisualizer,
            analyzer_visualizer: PAnalyzerVisualizer,
            objects: PStorage[PObject],
            paths: PStorage[PPath],
            measurables: PStorage[PMeasurable],
            experiments: PStorage[PExperiment],
    ):
        self.scanner = scanner
        self.analyzer = analyzer
        self.scanner_visualizer = scanner_visualizer
        self.analyzer_visualizer = analyzer_visualizer

        self.objects = objects
        self.paths = paths
        self.measurables = measurables
        self.experiments = experiments

    def tree(self) -> dict[str: list[PWidget]]:
        """
        Дерево проекта
        """
        tree = dict()

        scanner_widgets = []
        for widget in self.scanner.control_widgets:
            scanner_widgets.append(widget)
        tree['Scanner'] = scanner_widgets

        analyzer_widgets = []
        for widget in self.analyzer.control_widgets:
            analyzer_widgets.append(widget)
        tree['Analyzer'] = analyzer_widgets

        tree['Scanner graphics'] = self.scanner_visualizer.control_widgets
        tree['Analyzer graphics'] = self.analyzer_visualizer.control_widgets

        tree['Objects'] = [PWidget(name=w.name, widget=w.widget, icon=w.icon) for w in self.objects.data]
        tree['Paths'] = [PWidget(name=w.name, widget=w.widget, icon=w.icon) for w in self.paths.data]
        tree['Measurables'] = [PWidget(name=w.name, widget=w.widget, icon=w.icon) for w in self.measurables.data]
        tree['Experiments'] = [PWidget(name=w.name, widget=w.widget, icon=w.icon) for w in self.experiments.data]

        return tree




