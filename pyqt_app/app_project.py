from src.scanner.TRIM import TRIMScanner
from src.project import Project, PScannerSignals, PAnalyzerSignals, PStorage
from src.analyzers.rohde_schwarz import RohdeSchwarzAnalyzer, RohdeSchwarzEmulator
from src.project.PScanners import ToyScanner
from src.project.PAnalyzers import ToyAnalyser, ToySparam
from src.project.PExperiments import ToyExperiment
from src.project.PPaths import ToyPath
from src.scanner.TRIM import TRIM_emulator
from src.builder import AppBuilder

scanner_signals = PScannerSignals()
scanner = ToyScanner(
    instrument=TRIMScanner(ip="127.0.0.1", port=9006, signals=scanner_signals),
    signals=scanner_signals,
)
TRIM_emulator.run(blocking=False, motion_time=2, port=9006)  # use it only for emulating

analyzer_signals = PAnalyzerSignals()
analyzer = ToyAnalyser(
    # instrument=SocketAnalyzer(ip="192.168.5.168", port=9000, signals=analyzer_signals),
    instrument=RohdeSchwarzEmulator(ip="192.168.5.168", port="9000", signals=analyzer_signals),
    signals=analyzer_signals
)

objects = PStorage()
paths = PStorage()
measurands = PStorage()
experiments = PStorage()

paths.append(
    ToyPath(
        name=f'Path 1',
    )
)

paths.append(
    ToyPath(
        name=f'Path 2',
    )
)


experiments.append(
    ToyExperiment(
        scanner=scanner,
        name='Experiment 1'
    )
)

scanner_visualizer = None

analyzer_visualizer = None


project = Project(
    scanner=scanner,
    analyzer=analyzer,
    scanner_visualizer=scanner_visualizer,
    analyzer_visualizer=analyzer_visualizer,
    objects=objects,
    paths=paths,
    experiments=experiments,
    measurands=measurands,
    plots_1d=PStorage(),
    plots_2d=PStorage(),
    plots_3d=PStorage(),
    results=PStorage()
)

builder = AppBuilder(project=project)
