from src.scanner.TRIM import TRIMScanner
from src.project import Project, PScannerSignals, PAnalyzerSignals, PStorage
from src.analyzator.rohde_schwarz import RohdeSchwarzAnalyzer, RohdeSchwarzEmulator
from src.project.PScanners import ToyScanner, TRIMPScanner
from src.project.PAnalyzers import ToyAnalyser
from src.project.PExperiments import ToyExperiment
from src.project.PPaths import ToyPath
from src.scanner.TRIM import TRIM_emulator
from src.builder import AppBuilder, FactoryGroups
from src.ModelView import ModelViewFactory
from src import icons
from src.views.toy import ToyView, ToyScannerSettings, ToyScannerControl
from src.views.PScanners import TRIMControl, TRIMSettings
from src.views.PAnalyzers import SocketAnalyzerControl
import src.binds

scanner_signals = PScannerSignals()
scanner = TRIMPScanner(
    name="TRIM scanner",
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

paths = PStorage()
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
    objects=PStorage(),
    paths=paths,
    experiments=experiments,
    measurands=PStorage(),
    plots=PStorage(),
    results=PStorage()
)

AppBuilder.register_factory(
    ModelViewFactory(
        view_types=(TRIMControl, TRIMSettings,),
        model=scanner,
        icon=icons.scanner_icon
    ),
    group=FactoryGroups.scanners,
)

# AppBuilder.register_factory(
#     factory=ModelViewFactory(view_types=(ToyScannerSettings, ToyScannerControl,), model=scanner),
#     group=FactoryGroups.scanners
# )

AppBuilder.register_factory(
    factory=ModelViewFactory(
        view_types=(SocketAnalyzerControl,),
        model=analyzer,
        icon=icons.analyzer_icon
    ),
    group=FactoryGroups.analyzers,
)

builder = AppBuilder(project=project)
builder.restore_model_views()
builder.load_instruments()
