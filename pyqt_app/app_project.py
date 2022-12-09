from dataclasses import dataclass
from abc import ABC, abstractmethod
from PyQt6.QtCore import pyqtBoundSignal, QObject, pyqtSignal
from src.scanner.TRIM import TRIMScanner
from src.scanner import BaseAxes, Position, Velocity, Acceleration, Deceleration
from src.project import Project, PScannerSignals, PScanner, PAnalyzer, PAnalyzerSignals, PStorage
from src.project import PStorageSignals
from src.analyzator.rohde_schwarz.rohde_schwarz import RohdeSchwarzAnalyzator
from pyqt_app.PScanners import TRIMPScanner
from pyqt_app.PAnalyzers import RohdeSchwarzPAnalyzer
from pyqt_app.PVisualizers import PScannerVisualizer3D, PAnalyzerVisualizerRS
from PyQt6.QtWidgets import QTextEdit

objects = PStorage()
paths = PStorage()
experiments = PStorage()

scanner_signals = PScannerSignals()
scanner = TRIMPScanner(
    instrument=TRIMScanner(ip="127.0.0.1", port=9000, signals=scanner_signals),
    signals=scanner_signals,
)
scanner_visualizer = PScannerVisualizer3D(
    instrument=scanner,
    paths=paths,
    objects=objects,
)

analyzer_signals = PAnalyzerSignals()

analyzer = RohdeSchwarzPAnalyzer(
    instrument=RohdeSchwarzAnalyzator(ip="192.168.5.168", port="9000"),
    signals=analyzer_signals
)

analyzer_visualizer = PAnalyzerVisualizerRS(instrument=analyzer)


project = Project(
    scanner=scanner,
    analyzer=analyzer,
    scanner_visualizer=scanner_visualizer,
    analyzer_visualizer=analyzer_visualizer,
    objects=objects,
    paths=paths,
    experiments=experiments,
)

