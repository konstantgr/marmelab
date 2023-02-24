from src.scanner.TRIM import TRIMScanner
from src.project import Project, PScannerSignals, PAnalyzerSignals, PStorage
from src.analyzator.rohde_schwarz import RohdeSchwarzAnalyzer, RohdeSchwarzEmulator
from src.project.PScanners import ToyScanner
from src.project.PAnalyzers import ToyAnalyser
from src.project.PExperiments import ToyExperiment
from src.project.PPaths import ToyPath
from src.scanner.TRIM import TRIM_emulator
from src.Builder import AppBuilder, FactoryGroups
from src.ModelView import ModelViewFactory

from src.views.toy import ToyView, ToyScannerSettings, ToyScannerControl
import src.binds

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
    signals=analyzer_signals,
    name="Toy analyzer"
)

objects = PStorage()
paths = PStorage()
measurands = PStorage()
experiments = PStorage()

paths.append(
    ToyPath(
        name=f'path1',
    )
)

paths.append(
    ToyPath(
        name=f'path2',
    )
)

experiments.append(
    ToyExperiment(
        scanner=scanner,
        name='exp1'
    )
)

project = Project(
    scanner=scanner,
    analyzer=analyzer,
    objects=objects,
    paths=paths,
    experiments=experiments,
    measurands=measurands,
    plots=PStorage(),
    results=PStorage()
)

AppBuilder.register_factory(
    factory=ModelViewFactory(view_types=(ToyScannerSettings, ToyScannerControl,), model=scanner),
    group=FactoryGroups.scanners
)

AppBuilder.register_factory(
    factory=ModelViewFactory(view_types=(ToyView,), model=analyzer),
    group=FactoryGroups.analyzers
)

builder = AppBuilder(project=project)
builder.restore_model_views()
