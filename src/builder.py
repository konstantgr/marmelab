from .project.Project import Project, PScanner, PAnalyzer
from .ModelView import ModelViewFactory, ModelView_ViewTreeType, ModelView, ModelViewVisualizer, ModelViewVisualizerFactory
from typing import List, Dict, Union, Type, Tuple
from enum import Enum


def _check_cls(
        factory: ModelViewFactory,
        cls: Union[Type, Tuple[Type, ...]],):
    """Проверяет, является ли модель factory экземпляром класса cls"""
    if factory.model_type is not None:
        return issubclass(factory.model_type, cls)
    elif factory.model is not None:
        return isinstance(factory.model, cls)


class FactoryGroups(Enum):
    """Группы моделей"""
    scanners = "Scanners"
    analyzers = "Analyzers"
    visualizers = "Visualizers"
    objects = "Objects"
    paths = "Paths"
    measurands = "Measurands"
    rtplots = "Real-time plots"
    experiments = "Experiments"
    results = "Results"
    resplots = "Result plots"


class AppBuilder:
    """Контроллер """
    factories: Dict[FactoryGroups, List[ModelViewFactory]] = {group: [] for group in FactoryGroups}
    factory_by_type: Dict[type, ModelViewFactory] = {}
    scanner_visualizer_factory: ModelViewVisualizerFactory
    plots_visualizer_factory: ModelViewVisualizerFactory

    @classmethod
    def register_factory(cls, factory: ModelViewFactory, group: FactoryGroups):
        """Зарегистрировать фабрику ModelView"""
        cls.factories[group].append(factory)
        cls.factory_by_type[factory.type] = factory

    @classmethod
    def register_scanner_visualizer_factory(cls, factory: ModelViewVisualizerFactory):
        """Зарегистрировать фабрику ModelViewVisualizerFactory сканера"""
        cls.scanner_visualizer_factory = factory
        cls.register_factory(factory=factory, group=FactoryGroups.visualizers)

    @classmethod
    def register_plots_visualizer_factory(cls, factory: ModelViewVisualizerFactory):
        """Зарегистрировать фабрику ModelViewVisualizerFactory графиков"""
        cls.plots_visualizer_factory = factory
        cls.register_factory(factory=factory, group=FactoryGroups.visualizers)

    def __init__(
            self,
            project: Project
    ):
        self.project = project
        self.model_views: Dict[FactoryGroups, List[ModelView]] = {group: [] for group in FactoryGroups}
        for group, factories in AppBuilder.factories.items():
            for factory in factories:
                factory.connect_to_list(self.model_views[group])
        self._scanner_visualizer: ModelViewVisualizer = None
        self._plots_visualizer: ModelViewVisualizer = None

    def restore_model_views(self):
        """Create views for existing models"""
        for storage in self.project.get_storages():
            for model in storage.data:
                if type(model) not in AppBuilder.factory_by_type:
                    raise TypeError(f"Can't find any factory. Unknown model type {type(model)}.")
                factory = AppBuilder.factory_by_type[type(model)]
                factory.create(project=self.project, from_model=model)

    def load_instruments(self):
        """Load scanners and analyzers"""
        for scanner_factory in AppBuilder.factories[FactoryGroups.scanners]:
            scanner_factory.create(project=self.project)

        for analyzer_factory in AppBuilder.factories[FactoryGroups.analyzers]:
            analyzer_factory.create(project=self.project)

    def load_visualizers(self):
        """Load visualizers"""
        self._scanner_visualizer = AppBuilder.scanner_visualizer_factory.create(project=self.project)
        # self._plots_visualizer = AppBuilder.plots_visualizer_factory.create(project=self.project)

    @property
    def scanner_visualizer(self) -> ModelViewVisualizer:
        return self._scanner_visualizer

    @property
    def plots_visualizer(self) -> ModelViewVisualizer:
        return self._plots_visualizer

    def view_tree(self) -> Dict[str, List[ModelView_ViewTreeType]]:
        tree = dict()
        for group, model_views in self.model_views.items():
            tree[group.value] = [model_view.view_tree() for model_view in model_views]

        return tree
