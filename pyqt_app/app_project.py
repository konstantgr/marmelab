from src.scanner.TRIM import TRIMScanner
from src.project import Project, PScannerSignals, PAnalyzerSignals, PStorage
from src.analyzator.rohde_schwarz import RohdeSchwarzAnalyzer, RohdeSchwarzEmulator
from src.project.PScanners import TRIMPScanner
from src.project.PAnalyzers import RohdeSchwarzPAnalyzer
from src.analyzator.socket_analyzer.socket_analyzer import SocketAnalyzer
from src.project.PVisualizers import PScannerVisualizer3D, PAnalyzerVisualizerRS
from src.project.PMeasurables import MeasurableOfMeasurands
from src.project.PExperiments import Experiment
from src.project.PObjects import Object3d
from src.project.PPaths import Path3d
from src.scanner.TRIM import TRIM_emulator

scanner_signals = PScannerSignals()
scanner = TRIMPScanner(
    instrument=TRIMScanner(ip="127.0.0.1", port=9006, signals=scanner_signals),
    signals=scanner_signals,
)
TRIM_emulator.run(blocking=False, motion_time=2, port=9006)  # use it only for emulating

analyzer_signals = PAnalyzerSignals()
analyzer = RohdeSchwarzPAnalyzer(
    instrument=SocketAnalyzer(ip="192.168.5.168", port=9000, signals=analyzer_signals),
    # instrument=RohdeSchwarzEmulator(ip="192.168.5.168", port="9000", signals=analyzer_signals),
    signals=analyzer_signals
)

objects = PStorage()
paths = PStorage()
measurables = PStorage()
experiments = PStorage()

objects.append(
    Object3d(
        name='Object 1'
    )
)

paths.append(
    Path3d(
        name=f'Path 1',
        scanner=scanner
    )
)

measurables.append(
    MeasurableOfMeasurands(
        analyzer=analyzer,
        name='Meas 1',
    )
)
measurables.append(
    MeasurableOfMeasurands(
        analyzer=analyzer,
        name='Meas 2',
    )
)

experiments.append(
    Experiment(
        name='Experiment 1',
        p_analyzer=analyzer,
        p_scanner=scanner,
        p_paths=paths,
        p_measurements=measurables,
    )
)

scanner_visualizer = PScannerVisualizer3D(
    scanner=scanner,
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
