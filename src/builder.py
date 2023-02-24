from .project.Project import Project, PBaseTypes
from .project.Project import PPath, PObject, PMeasurand, PResults, PExperiment, PPlot1D, PPlot2D, PPlot3D
from .ModelView import ModelViewFactory, ModelView_ViewTreeType, ModelView
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
    scanners = "Scanners"
    analyzers = "Analyzers"
    objects = "Objects"
    paths = "Paths"
    measurands = "Measurands"
    rtplots = "Real-time plots"
    experiments = "Experiments"
    results = "Results"
    resplots = "Result plots"


class AppBuilder:
    factories: Dict[FactoryGroups, List[ModelViewFactory]] = {group: [] for group in FactoryGroups}
    group_by_factory: Dict[ModelViewFactory, FactoryGroups] = {}
    factory_by_type: Dict[type, ModelViewFactory] = {}

    @classmethod
    def register_factory(cls, factory: ModelViewFactory, group: FactoryGroups):
        """Зарегистрировать фабрику ModelView"""
        cls.factories[group].append(factory)
        cls.group_by_factory[factory] = group
        cls.factory_by_type[factory.type]  = factory

    def __init__(
            self,
            project: Project
    ):
        self.project = project
        self.model_views: Dict[FactoryGroups, List[ModelView]] = {group: [] for group in FactoryGroups}
        for group, factories in AppBuilder.factories.items():
            for factory in factories:
                factory.connect_to_list(self.model_views[group])

    def restore_model_views(self):
        for storage in self.project.get_storages():
            for model in storage.data:
                if type(model) not in AppBuilder.factory_by_type:
                    raise TypeError(f"Can't find any factory. Unknown model type {type(model)}.")
                factory = AppBuilder.factory_by_type[type(model)]
                factory.create(project=self.project, from_model=model)

    def view_tree(self) -> Dict[str, List[ModelView_ViewTreeType]]:
        tree = dict()
        for group, model_views in self.model_views.items():
            tree[group.value] = [model_view.view_tree() for model_view in model_views]

        return tree
