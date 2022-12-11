import abc

from ..scanner import Scanner, ScannerSignals
from ..analyzator import AnalyzerSignals, BaseAnalyzator
from ..scanner import BaseAxes, Position, Velocity, Acceleration, Deceleration
from PyQt6.QtCore import pyqtBoundSignal, pyqtSignal, QObject
from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QIcon
from dataclasses import dataclass, field
from abc import abstractmethod
from typing import Union
from .icons import path_icon, object_icon


def _meta_resolve(cls):
    class _MetaResolver(type(QObject), type(cls)):
        # https://stackoverflow.com/questions/28720217/multiple-inheritance-metaclass-conflict
        pass
    return _MetaResolver


@dataclass
class PWidget:
    name: str
    widget: QWidget
    icon: QIcon = None


class PScannerSignals(QObject, ScannerSignals, metaclass=_meta_resolve(ScannerSignals)):
    position: pyqtBoundSignal = pyqtSignal([BaseAxes], [Position])
    velocity: pyqtBoundSignal = pyqtSignal([BaseAxes], [Velocity])
    acceleration: pyqtBoundSignal = pyqtSignal([BaseAxes], [Acceleration])
    deceleration: pyqtBoundSignal = pyqtSignal([BaseAxes], [Deceleration])
    is_connected: pyqtBoundSignal = pyqtSignal(bool)
    set_settings: pyqtBoundSignal = pyqtSignal(dict)
    stop: pyqtBoundSignal = pyqtSignal()
    abort: pyqtBoundSignal = pyqtSignal()
    connect: pyqtBoundSignal = pyqtSignal()
    disconnect: pyqtBoundSignal = pyqtSignal()
    home: pyqtBoundSignal = pyqtSignal()


class PScanner(abc.ABC):
    def __init__(
            self,
            instrument: Scanner,
            signals: PScannerSignals,
    ):
        self.signals = signals
        self.instrument = instrument

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
        pass

    @property
    @abstractmethod
    def control_widgets(self) -> list[PWidget]:
        pass


class PAnalyzerSignals(QObject, AnalyzerSignals, metaclass=_meta_resolve(AnalyzerSignals)):
    data: pyqtBoundSignal = pyqtSignal(dict)
    connect: pyqtBoundSignal = pyqtSignal()
    disconnect: pyqtBoundSignal = pyqtSignal()
    set_settings: pyqtBoundSignal = pyqtSignal(dict)
    is_connected: pyqtBoundSignal = pyqtSignal(bool)


class PAnalyzer(abc.ABC):
    def __init__(
            self,
            signals: PAnalyzerSignals,
            instrument: BaseAnalyzator,
    ):
        self.signals = signals
        self.instrument = instrument

        self.signals.connect.connect(self.instrument.connect)
        self.signals.disconnect.connect(self.instrument.disconnect)
        self.signals.set_settings.connect(self._set_settings)

    def _set_settings(self, d: dict):
        pass
        # self.instrument.set_settings(**d)

    @property
    @abstractmethod
    def control_widgets(self) -> list[PWidget]:
        pass


class PAnalyzerVisualizer(abc.ABC):
    def __init__(
            self,
            instrument: PAnalyzer
    ):
        self.instrument = instrument

    @property
    @abstractmethod
    def widget(self) -> QWidget:
        pass

    @property
    @abstractmethod
    def control_widgets(self) -> list[PWidget]:
        pass


@dataclass
class PBase:
    name: str
    widget: QWidget
    icon: QIcon = None


@dataclass
class PExperiment(PBase):
    pass


@dataclass
class PMeasurand(PBase):
    pass


@dataclass
class PObject(PBase):
    icon: QIcon = object_icon


@dataclass
class PPath(PBase):
    icon: QIcon = path_icon


class PStorageSignals(QObject):
    changed: pyqtBoundSignal = pyqtSignal()
    add: pyqtBoundSignal = pyqtSignal(PBase)
    delete: pyqtBoundSignal = pyqtSignal(PBase)


@dataclass
class PStorage:
    signals: PStorageSignals = field(default_factory=PStorageSignals)
    data: list[Union[PBase, PExperiment, PMeasurand, PObject, PPath]] = field(default_factory=list)

    def __post_init__(self):
        self.signals.add.connect(self.append)
        self.signals.delete.connect(self.delete)

    def append(self, x: PBase):
        self.data.append(x)
        self.signals.changed.emit()

    def delete(self, x: PBase):
        self.data.remove(x)
        self.signals.changed.emit()


class Project:
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




