from src.project.PExperiments import Experiment
from src.scanner.TRIM import TRIMScanner
from src.project import Project, PScannerSignals, PAnalyzerSignals, PStorage
from src.analyzers.rohde_schwarz import RohdeSchwarzAnalyzer, RohdeSchwarzEmulator
from src.analyzers.ceyear_analyzer.ceyear_emulator import CeyearAnalyzerEmulator
from src.project.PScanners import ToyScanner, TRIMPScanner
from src.project.PAnalyzers import ToyAnalyser, ToySparam
from src.project.PPaths import ToyPath
from src.project.PAnalyzers.ceyear import CeyearPAnalyzer, SParams
from src.project.PPaths import ToyPath, TablePathModel
from src.project.PMeasurands.time_measurand import TimeMeas
from src.scanner.TRIM import TRIM_emulator
from src.builder import AppBuilder, FactoryGroups
from src.ModelView import ModelViewFactory, ModelViewVisualizerFactory
from src import icons
from src.project.PVisualizers import xyzwScannerVisualizer, PAnalyzerVisualizerModel
from src.views.toy import ToyView, ToyScannerSettings, ToyScannerControl
from src.views.PScannerVisualizers.xyzw import xyzwSettings, xyzwWidget
from src.views.PScanners import TRIMControl, TRIMSettings
from src.views.PAnalyzers import SocketAnalyzerControl
from src.views.PMeasurands import SParamsView, TimeView
from src.views.PPlotVisualizer import PlotsView
import src.binds

scanner_signals = PScannerSignals()
scanner = TRIMPScanner(
    name="TRIM scanner",
    instrument=TRIMScanner(ip="127.0.0.1", port=9008, signals=scanner_signals),
    signals=scanner_signals,
)
TRIM_emulator.run(blocking=False, motion_time=2, port=9008)  # use it only for emulating

analyzer_signals = PAnalyzerSignals()
analyzer = CeyearPAnalyzer(
    # instrument=SocketAnalyzer(ip="192.168.5.168", port=9000, signals=analyzer_signals),
    instrument=CeyearAnalyzerEmulator(ip="192.168.5.168", port="9000", signals=analyzer_signals),
    signals=analyzer_signals
)

objects = PStorage()
paths = PStorage()
experiments = PStorage()
plots = PStorage()
measurands = PStorage()

scanner_visualizer = xyzwScannerVisualizer(
    name="Scanner visualizer",
    scanner=scanner,
    objects=objects,
    paths=paths,
)

analyzer_visualizer = PAnalyzerVisualizerModel(
    name="Plots visualizer",
    plots=plots,
    # scanner=scanner,
    # objects=objects,
    # paths=paths,
)

paths.append(
    TablePathModel(
        name=f'path1',
        scanner=scanner
    )
)

measurands.append(
    SParams(
        name='meas1',
        panalyzer=analyzer
    )
)

project = Project(
    scanner=scanner,
    analyzer=analyzer,
    objects=objects,
    paths=paths,
    experiments=experiments,
    measurands=measurands,
    plots=plots,
    results=PStorage(),
    scanner_visualizer=scanner_visualizer,
    app_builder=AppBuilder
)
experiments.append(
    Experiment(
        scanner=scanner,
        name='exp1',
        paths=paths,
        measurands=measurands,
        app_builder=AppBuilder,
        project=project
    )
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

AppBuilder.register_plots_visualizer_factory(
    factory=ModelViewVisualizerFactory(
        view_types=(),
        model=analyzer_visualizer,
        visualizer_widget_type=PlotsView,
    )
)

AppBuilder.register_factory(
    factory=ModelViewFactory(
        view_types=(SParamsView,),
        model_type=SParams,
        icon=icons.s_params,
    ),
    group=FactoryGroups.measurands,
)

AppBuilder.register_factory(
    factory=ModelViewFactory(
        view_types=(TimeView,),
        model_type=TimeMeas,
        icon=icons.s_params,
    ),
    group=FactoryGroups.measurands,
)

builder_ = AppBuilder(project=project)
builder_.restore_model_views()
builder_.load_instruments()
builder_.load_visualizers()
builder = builder_
