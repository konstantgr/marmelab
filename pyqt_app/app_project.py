from src.scanner.TRIM import TRIMScanner
from src.project import Project, PScannerSignals, PAnalyzerSignals, PStorage
from src.analyzers.rohde_schwarz import RohdeSchwarzAnalyzer, RohdeSchwarzEmulator
from src.project.PScanners import ToyScanner, TRIMPScanner
from src.project.PAnalyzers import ToyAnalyser, ToySparam
from src.project.PExperiments import ToyExperiment
from src.project.PPaths import ToyPath, TablePathModel
from src.scanner.TRIM import TRIM_emulator
from src.builder import AppBuilder, FactoryGroups
from src.ModelView import ModelViewFactory, ModelViewVisualizerFactory
from src import icons
from src.project.PVisualizers import xyzwScannerVisualizer
from src.views.toy import ToyView, ToyScannerSettings, ToyScannerControl
from src.views.PScannerVisualizers.xyzw import xyzwSettings, xyzwWidget
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

objects = PStorage()
paths = PStorage()
experiments = PStorage()

scanner_visualizer = xyzwScannerVisualizer(
    name="Scanner visualizer",
    scanner=scanner,
    objects=objects,
    paths=paths,
)
paths.append(
    TablePathModel(
        name=f'Table path 1',
        scanner=scanner
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
    measurands=PStorage(),
    plots=PStorage(),
    results=PStorage(),
    scanner_visualizer=scanner_visualizer
)

AppBuilder.register_factory(
    ModelViewFactory(
        view_types=(TRIMControl, TRIMSettings,),
        model=scanner,
        icon=icons.scanner_icon,
        removable=False,
        reproducible=False
    ),
    group=FactoryGroups.scanners,
)

AppBuilder.register_factory(
    factory=ModelViewFactory(
        view_types=(SocketAnalyzerControl,),
        model=analyzer,
        icon=icons.analyzer_icon,
        removable=False,
        reproducible=False
    ),
    group=FactoryGroups.analyzers,
)

AppBuilder.register_scanner_visualizer_factory(
    factory=ModelViewVisualizerFactory(
        view_types=(xyzwSettings,),
        model=scanner_visualizer,
        visualizer_widget_type=xyzwWidget,
    )
)

builder_ = AppBuilder(project=project)
builder_.restore_model_views()
builder_.load_instruments()
builder_.load_visualizers()
builder = builder_
