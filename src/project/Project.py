import abc

from ..scanner import Scanner, ScannerSignals
from ..analyzator import AnalyzerSignals, BaseAnalyzer
from ..scanner import BaseAxes, Position, Velocity, Acceleration, Deceleration
from PyQt6.QtCore import pyqtBoundSignal, pyqtSignal, QObject
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QIcon
from dataclasses import dataclass, field
from abc import abstractmethod
from typing import Union, Callable
from .icons import path_icon, object_icon


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
    name: str
    widget: QWidget
    icon: QIcon = None


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
    is_connected: PState
    is_moving: PState
    is_in_use: PState  # используется в эксперименте прямо сейчас


class PScanner(abc.ABC):
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


class PScannerVisualizer(abc.ABC):
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


class PAnalyzer(abc.ABC):
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
        pass
        # self.instrument.set_settings(**d)

    @property
    @abstractmethod
    def control_widgets(self) -> list[PWidget]:
        """
        Виджеты, управляющие анализатором
        """


class PAnalyzerVisualizer(abc.ABC):
    """
    Класс визуализатора анализатора
    """
    def __init__(
            self,
            instrument: PAnalyzer
    ):
        self.instrument = instrument

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


class PBaseSignals(QObject):
    changed: pyqtBoundSignal = pyqtSignal()


@dataclass
class PBase:
    """
    Базовый класс всех объектов в проекте
    """
    name: str
    widget: QWidget
    icon: QIcon = None
    signals: PBaseSignals = field(default_factory=PBaseSignals)


@dataclass
class PExperiment(PBase):
    """
    Класс эксперимента
    """


@dataclass
class PMeasurand(PBase):
    """
    Класс измеряемой величины
    """

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


class PStorageSignals(QObject):
    """
    Сигналы хранилища
    """
    changed: pyqtBoundSignal = pyqtSignal()
    element_changed: pyqtBoundSignal = pyqtSignal()
    add: pyqtBoundSignal = pyqtSignal(PBase)
    delete: pyqtBoundSignal = pyqtSignal(PBase)


@dataclass
class PStorage:
    """
    Базовое хранилище объектов проекта
    """
    signals: PStorageSignals = field(default_factory=PStorageSignals)
    data: list[Union[PBase, PExperiment, PMeasurand, PObject, PPath]] = field(default_factory=list)

    def __post_init__(self):
        self.signals.add.connect(self.append)
        self.signals.delete.connect(self.delete)

    def append(self, x: PBase):
        """
        Добавить элемент в хранилище
        """
        self.data.append(x)
        x.signals.changed.connect(self._element_changed_emit)
        self.signals.changed.emit()

    def delete(self, x: PBase):
        """
        Удалить элемент из хранилища
        """
        x.signals.changed.disconnect()
        self.data.remove(x)
        self.signals.changed.emit()

    def _element_changed_emit(self):
        self.signals.element_changed.emit()


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
            objects: PStorage = None,
            paths: PStorage = None,
            experiments: PStorage = None,
    ):
        self.scanner = scanner
        self.analyzer = analyzer
        self.scanner_visualizer = scanner_visualizer
        self.analyzer_visualizer = analyzer_visualizer

        self.objects = objects if objects is not None else PStorage()
        self.paths = paths if paths is not None else PStorage()
        self.experiments = experiments if experiments is not None else PStorage()

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
        tree['Experiments'] = [PWidget(name=w.name, widget=w.widget, icon=w.icon) for w in self.experiments.data]

        return tree




