"""
Реализация билдера приложения
"""

from .project import Project
from .project.PScanners import ToyScanner
from .project.PAnalyzers import ToyAnalyser
from .project.PPaths import ToyPath
from .project.PExperiments import ToyExperiment
from .project.Project import PBaseTypes, PBase, PStorage, PScannerTypes, PAnalyzerTypes
# from .project.PVisualizers.ScannerVisualizer import ScannerVisualizer
# from .project.PVisualizers.AnalyzerVisualizer import PAnalyzerVisualizerRS

from .views.toy import ToyView, ToyScannerControl, ToyScannerSettings
from .views.View import BaseView
from dataclasses import dataclass
from PyQt6.QtWidgets import QWidget
from typing import Union, Type, List, Tuple, Any
from enum import Enum

BINDS = {
    ToyScanner: [ToyScannerControl, ToyScannerSettings],
    ToyAnalyser: [ToyScannerControl, ToyScannerSettings],
    ToyPath: ToyView,
    ToyExperiment: ToyView,
    # ScannerVisualizer: ToyView,
    # PAnalyzerVisualizerRS: ToyView
}




class ModelView:
    def __init__(
            self,
            model: PBaseTypes,
            views: List[BaseView]
    ):
        self.model = model
        self.view = views


class ModelViewFactory:
    def __init__(
            self,
            view_types: List[Type[BaseView]],
            model: PBaseTypes = None,
            model_type: Type[PBaseTypes] = None,
            model_project_args: Tuple[str, ...] = None,
            model_kwargs: dict[str, Any] = None,
    ):
        self.view_types = view_types
        self.model_type = model_type
        self.model_kwargs = model_kwargs
        self.model = model
        if (self.model is None and self.model_type is None) or (self.model is not None and self.model_type is not None):
            raise ValueError("Only one of model and model_type has to be None")

    def create(self) -> ModelView:
        """Creates ModelView instance"""
        model = self.model_type(**self.model_kwargs) if self.model is None else self.model
        return ModelView(
            model=model,
            views=[view_cl(model) for view_cl in self.view_types]
        )


class GroupOfModelView:
    def __init__(
            self,
            name: str,
            model_view_factory: Union[ModelViewFactory, 'GroupOfModelView'],
            storage: PStorage = None
    ):
        self.model_view_factory = model_view_factory
        self.storage = storage
        self.model_views: List[ModelView] = []
        self.name = name

    def create(self) -> ModelView:
        """Creates ModelView instance"""
        model_view = self.model_view_factory.create()
        if self.storage is not None and isinstance(self.model_view_factory, ModelViewFactory):
            self.storage.append(model_view.model)
        self.model_views.append(model_view)
        return model_view


class AppBuilder:



# class AppBuilder:
#     def __init__(
#             self,
#             project: Project
#     ):
#         self.project = project
#         self.models_with_widgets = {}
#
#     def _create_widget(self, model):
#         print(model.__class__)
#         if model in self.models_with_widgets.keys():
#             return self.models_with_widgets[model]
#
#         bind = BINDS[model.__class__]
#         if isinstance(bind, list):
#             res = []
#             for b in bind:
#                 res.append(b(model=model))
#         else:
#             res = bind(model=model)
#
#         self.models_with_widgets[model] = res
#         return res
#
#     def tree(self) -> dict[str: list[Union[QWidget, list[QWidget]]]]:
#         """
#         Создать новое дерево проекта
#         """
#         tree = dict()
#
#         tree['Scanners'] = [self._create_widget(self.project.scanner)]
#         tree['Analyzers'] = [self._create_widget(self.project.analyzer)]
#
#         # tree['Scanner graphics'] = self.scanner_visualizer.control_widgets
#         # tree['Analyzer graphics'] = self.analyzer_visualizer.control_widgets
#
#         tree['Paths'] = []
#         for model in self.project.paths.data:
#             tree['Paths'].append(self._create_widget(model))
#
#         tree['Measurands'] = []
#         for model in self.project.measurands.data:
#             tree['Measurands'].append(self._create_widget(model))
#
#         tree['Real-time plots'] = []
#
#         tree['Experiments'] = []
#         for model in self.project.experiments.data:
#             tree['Experiments'].append(self._create_widget(model))
#
#         tree['Results'] = []
#         tree['Result plots'] = []
#
#         return tree
