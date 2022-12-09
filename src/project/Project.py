import abc

from src.scanner import Scanner, ScannerSignals
from src.analyzator import AnalyzerSignals, BaseAnalyzator
from src.scanner import BaseAxes, Position, Velocity, Acceleration, Deceleration
from PyQt6.QtCore import pyqtBoundSignal, pyqtSignal, QObject
from PyQt6.QtWidgets import QWidget
from dataclasses import dataclass, field
from abc import abstractmethod


def _meta_resolve(cls):
    class _MetaResolver(type(QObject), type(cls)):
        # https://stackoverflow.com/questions/28720217/multiple-inheritance-metaclass-conflict
        pass
    return _MetaResolver


@dataclass
class PWidget:
    name: str
    widget: QWidget


class PScannerSignals(QObject, ScannerSignals, metaclass=_meta_resolve(ScannerSignals)):
    position: pyqtBoundSignal = pyqtSignal([BaseAxes], [Position])
    velocity: pyqtBoundSignal = pyqtSignal([BaseAxes], [Velocity])
    acceleration: pyqtBoundSignal = pyqtSignal([BaseAxes], [Acceleration])
    deceleration: pyqtBoundSignal = pyqtSignal([BaseAxes], [Deceleration])
    set_settings: pyqtBoundSignal = pyqtSignal(dict)
    stop: pyqtBoundSignal = pyqtSignal()
    abort: pyqtBoundSignal = pyqtSignal()
    connect: pyqtBoundSignal = pyqtSignal()
    disconnect: pyqtBoundSignal = pyqtSignal()
    home: pyqtBoundSignal = pyqtSignal()


class PScanner(abc.ABC):
    def __init__(
            self,
            signals: PScannerSignals,
            instrument: Scanner,
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


class PBase:
    pass


class PExperiment(PBase):
    pass


class PMeasurand(PBase):
    pass


class PObject(PBase):
    pass


class PPath(PBase):
    pass


class PStorageSignals(QObject):
    changed: pyqtBoundSignal = pyqtSignal()
    add: pyqtBoundSignal = pyqtSignal(PBase)
    delete: pyqtBoundSignal = pyqtSignal(PBase)


class PStorage:
    def __init__(self):
        self.signals: PStorageSignals = PStorageSignals()
        self._data = []
        self.signals.add.connect(self.append)
        self.signals.delete.connect(self.delete)

    def append(self, x: PBase):
        self._data.append(x)
        self.signals.changed.emit()

    def delete(self, x: PBase):
        self._data.remove(x)
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

    def create_tree(self):
        tree = []

        scanner_widgets = []
        for widget in self.scanner.control_widgets:
            scanner_widgets.append(widget.widget)
        tree.append(scanner_widgets)

        analyzer_widgets = []
        for widget in self.analyzer.control_widgets:
            analyzer_widgets.append(widget.widget)
        tree.append(analyzer_widgets)


