from dataclasses import dataclass
from abc import ABC, abstractmethod
from PyQt6.QtCore import pyqtBoundSignal, QObject, pyqtSignal
from src.scanner.TRIM import TRIMScanner
from src.scanner import BaseAxes, Position, Velocity, Acceleration, Deceleration
from src.Project import Project, PScannerSignals, PScanner, PAnalyzer, PAnalyzerSignals
from src.analyzator.rohde_schwarz.rohde_schwarz import RohdeSchwarzAnalyzator
from .PScanners import TRIMPScanner

scanner_signals = PScannerSignals()
scanner = TRIMPScanner(
    instrument=TRIMScanner(ip="127.0.0.1", port=9000, signals=scanner_signals),
    signals=scanner_signals,
)


analyzer_signals = PAnalyzerSignals()
analyzer = PAnalyzer(
    instrument=RohdeSchwarzAnalyzator(ip="192.168.5.168", port="9000"),
    signals=analyzer_signals
)


project = Project(
    scanner=scanner,
    analyzer=analyzer,

)
