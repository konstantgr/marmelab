from src.scanner.TRIM import TRIMScanner
from src.project import Project, PScannerSignals, PAnalyzerSignals, PStorage
from src.analyzator.rohde_schwarz.rohde_schwarz import RohdeSchwarzAnalyzator
from src.project.PScanners import TRIMPScanner
from src.project.PAnalyzers import RohdeSchwarzPAnalyzer
from PVisualizers import PScannerVisualizer3D, PAnalyzerVisualizerRS
from PyQt6.QtWidgets import QTextEdit
from src.project.PObjects import Object3d
from src.project.PPaths import Path3d
import numpy as np
from src.project.PStorages import ObjectsStorage3d, PathsStorage3d, ExperimentsStorage


objects = ObjectsStorage3d()
paths = PathsStorage3d()
experiments = ExperimentsStorage()

objects.append(Object3d(name='Object 1'))
paths.append(Path3d(
    name='Path 1',
    points=np.array([[1000*i, 0, 0] for i in range(5)])
))

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

