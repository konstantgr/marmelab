from src.scanner.TRIM import TRIMScanner
from src.project import Project, PScannerSignals, PAnalyzerSignals, PStorage
from src.analyzator.rohde_schwarz import RohdeSchwarzAnalyzer, RohdeSchwarzEmulator
from src.project.PScanners import TRIMPScanner
from src.project.PAnalyzers import RohdeSchwarzPAnalyzer
from src.project.PVisualizers import PScannerVisualizer3D, PAnalyzerVisualizerRS
from src.project.PMeasurables import MeasurableOfMeasurands
from PyQt6.QtWidgets import QTextEdit
from src.project.PObjects import Object3d
from src.project.PPaths import Path3d
import numpy as np
from src.project.PStorages import ObjectsStorage3d, PathsStorage3d, ExperimentsStorage
from src.scanner.TRIM import TRIM_emulator
from src.project.Project import PScannerStates

scanner_signals = PScannerSignals()
scanner = TRIMPScanner(
    instrument=TRIMScanner(ip="127.0.0.1", port=9005, signals=scanner_signals),
    signals=scanner_signals,
)
TRIM_emulator.run(blocking=False, motion_time=2, port=9005)  # use it only for emulating

analyzer_signals = PAnalyzerSignals()
analyzer = RohdeSchwarzPAnalyzer(
    # instrument=RohdeSchwarzAnalyzer(ip="192.168.5.168", port="9000"),
    instrument=RohdeSchwarzEmulator(ip="192.168.5.168", port="9000", signals=analyzer_signals),
    signals=analyzer_signals
)

objects = ObjectsStorage3d()
paths = PathsStorage3d()
measurables = PStorage()
experiments = ExperimentsStorage()

objects.append(
    Object3d(
        name='Object 1'
    )
)

paths.append(
    Path3d(
        name=f'Path 1',
        points=np.array([[1000*i, 0, 0] for i in range(5)]),
        scanner=scanner
    )
)

measurables.append(
    MeasurableOfMeasurands(
        measurands=analyzer.get_measurands(),
        name='Meas 1',
    )
)
measurables.append(
    MeasurableOfMeasurands(
        measurands=analyzer.get_measurands(),
        name='Meas 2',
    )
)

scanner_visualizer = PScannerVisualizer3D(
    instrument=scanner,
    paths=paths,
    objects=objects,
)

analyzer_visualizer = PAnalyzerVisualizerRS(
    measurables=measurables,
    instrument_states=analyzer.states,
)


project = Project(
    scanner=scanner,
    analyzer=analyzer,
    scanner_visualizer=scanner_visualizer,
    analyzer_visualizer=analyzer_visualizer,
    objects=objects,
    paths=paths,
    experiments=experiments,
    measurables=measurables
)
