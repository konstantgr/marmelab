from ..scanner import Scanner, ScannerSignals
from ..analyzator import AnalyzerSignals, BaseAnalyzer
from ..scanner import BaseAxes, Position, Velocity, Acceleration, Deceleration
from PyQt6.QtCore import pyqtBoundSignal, pyqtSignal, QObject
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QIcon
from dataclasses import dataclass, field
from abc import abstractmethod, ABC, ABCMeta
from typing import Union, Callable, Generic, TypeVar, Any, Type
from .icons import path_icon, object_icon, base_icon
from pyqtgraph import PlotWidget, GraphicsLayoutWidget


def _meta_resolve(cls):
    class _MetaResolver(type(QObject), type(cls)):
        # https://stackoverflow.com/questions/28720217/multiple-inheritance-metaclass-conflict
        pass
    return _MetaResolver


class PWidget:
    """
    Класс виджетов управления
    """
    def __init__(
            self,
            name: str,
            widget: QWidget,
            icon: QIcon = None
    ):
        self.name = name
        self.widget = widget
        self.icon = icon


class PBaseSignals(QObject):
    """Сигналы PBase"""
    changed: pyqtBoundSignal = pyqtSignal()


class PBase:
    """
    Базовый класс всех объектов в проекте
    """
    icon: QIcon = base_icon

    def __init__(
            self,
            name: str,
            widget: QWidget,
    ):
        self.name = name
        self.widget = widget
        self.signals = PBaseSignals()


class PObject(PBase):
    """
    Класс объекта исследования
    """
    icon: QIcon = object_icon


class PPath(PBase, metaclass=ABCMeta):
    """
    Класс пути перемещения сканера
    """
    icon: QIcon = path_icon

    @abstractmethod
    def get_points(self) -> list[Position]:
        """
        Возвращает все точки в виде листа из последовательных позиций
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
    Класс сканера, объединяющего сам сканер, его состояния и сигналы
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
            scanner: PScanner
    ):
        self.scanner = scanner

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


class PAnalyzer(ABC):
    """
    Класс анализатора, объединяющий сигналы и статусы анализатора.
    Важное правило: к атрибуту instrument иметь доступ должны только модели, но не вьюшки!
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
        self.current_measurand: Union[PMeasurand, None] = None  # измерение, к которому подготовлен анализатор

        self.signals.connect.connect(self.instrument.connect)
        self.signals.disconnect.connect(self.instrument.disconnect)
        self.signals.set_settings.connect(self._set_settings)

    def _set_settings(self, d: dict):
        self.current_measurand = None
        self.instrument.set_settings(**d)

    def set_current_measurand(self, measurand: PMeasurand):
        """Объявить """
        self.current_measurand = measurand

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


class PMeasurable(PBase, metaclass=ABCMeta):
    """
    Класс измеряемой величины
    """
    def __init__(
            self,
            name: str,
            widget: QWidget
    ):
        super(PMeasurable, self).__init__(
            name=name,
            widget=widget,
        )

    @abstractmethod
    def measure(self) -> Any:
        """Проводит измерение при помощи инструмента и возвращает результат"""

    @property
    def plot_widget(self) -> Union[PlotWidget, GraphicsLayoutWidget, None]:
        return None


class PExperiment(PBase):
    """
    Класс эксперимента
    """


class PStorageSignals(QObject):
    """
    Сигналы хранилища
    """
    changed: pyqtBoundSignal = pyqtSignal()  # эмит при .add() и .delete()
    add: pyqtBoundSignal = pyqtSignal(PBase)
    delete: pyqtBoundSignal = pyqtSignal(PBase)


PBaseTypes = TypeVar('PBaseTypes', PBase, PExperiment, PMeasurable, PObject, PPath)


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




