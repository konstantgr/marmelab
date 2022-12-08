import abc

from src.scanner import Scanner, ScannerSignals
from src.analyzator import AnalyzerSignals, BaseAnalyzator
from src.scanner import BaseAxes, Position, Velocity, Acceleration, Deceleration
from PyQt6.QtCore import pyqtBoundSignal, pyqtSignal, QObject
from PyQt6.QtWidgets import QWidget
from dataclasses import dataclass
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
    position = pyqtSignal([BaseAxes], [Position])
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


class PExperiment:
    pass


class PMeasurand:
    pass


class PObject:
    pass


class PPath:
    pass


class Project:
    def __init__(
            self,
            scanner: PScanner,
            analyzer: PAnalyzer,
            scanner_visualizer: PScannerVisualizer,
            analyzer_visualizer: PAnalyzerVisualizer,
            objects: list[PObject] = None,
            paths: list[PPath] = None,
            experiments: list[PExperiment] = None,
    ):
        self.scanner = scanner
        self.analyzer = analyzer
        self.scanner_visualizer = scanner_visualizer
        self.analyzer_visualizer = analyzer_visualizer

        self.objects = objects if objects is not None else []
        self.paths = paths if paths is not None else []
        self.experiments = experiments if experiments is not None else []

