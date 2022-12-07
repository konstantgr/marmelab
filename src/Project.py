from dataclasses import dataclass
from abc import ABC, abstractmethod
from PyQt6.QtCore import pyqtBoundSignal, QObject, pyqtSignal


class ScannerSignals(QObject):
    """
    Класс сигналов для сканера
    """
    position_signal = pyqtSignal([BaseAxes], [Position])
    velocity_signal: pyqtBoundSignal = pyqtSignal([BaseAxes], [Velocity])
    acceleration_signal: pyqtBoundSignal = pyqtSignal([BaseAxes], [Acceleration])
    deceleration_signal: pyqtBoundSignal = pyqtSignal([BaseAxes], [Deceleration])
    set_settings: pyqtBoundSignal = pyqtSignal(dict)


class PScanner:
    pass


class PScannerVisualizer:
    pass


class PAnalyzer:
    pass


class PAnalyzerVisualizer:
    pass


class Project:
    def __init__(self):
        self.scanner = PScanner()
        self.analyzer = PAnalyzer()
        self.scanner_visualizer = PScannerVisualizer()
        self.analyzer_visualizer = PAnalyzerVisualizer()
