"""
Реализация билдера приложения
"""

from .project import Project
from .project.PScanners import ToyScanner
from .project.PAnalyzers import ToyAnalyser
from .project.PPaths import ToyPath
from .project.PExperiments import ToyExperiment
# from .project.PVisualizers.ScannerVisualizer import ScannerVisualizer
# from .project.PVisualizers.AnalyzerVisualizer import PAnalyzerVisualizerRS

from .views.toy import ToyView, ToyScannerControl, ToyScannerSettings
from .views.View import BaseView

from PyQt6.QtWidgets import QWidget
from typing import Union, Type

BINDS = {
    ToyScanner: [ToyScannerControl, ToyScannerSettings],
    ToyAnalyser: [ToyScannerControl, ToyScannerSettings],
    ToyPath: ToyView,
    ToyExperiment: ToyView,
    # ScannerVisualizer: ToyView,
    # PAnalyzerVisualizerRS: ToyView
}


class AppBuilder:
    def __init__(
            self,
            project: Project
    ):
        self.project = project
        self.models_with_widgets = {}

    def _create_widget(self, model):
        print(model.__class__)
        if model in self.models_with_widgets.keys():
            return self.models_with_widgets[model]

        bind = BINDS[model.__class__]
        if isinstance(bind, list):
            res = []
            for b in bind:
                res.append(b(model=model))
        else:
            res = bind(model=model)

        self.models_with_widgets[model] = res
        return res

    def tree(self) -> dict[str: list[Union[QWidget, list[QWidget]]]]:
        """
        Создать новое дерево проекта
        """
        tree = dict()

        tree['Scanners'] = [self._create_widget(self.project.scanner)]
        tree['Analyzers'] = [self._create_widget(self.project.analyzer)]

        # tree['Scanner graphics'] = self.scanner_visualizer.control_widgets
        # tree['Analyzer graphics'] = self.analyzer_visualizer.control_widgets

        tree['Paths'] = []
        for model in self.project.paths.data:
            tree['Paths'].append(self._create_widget(model))

        tree['Measurands'] = []
        for model in self.project.measurands.data:
            tree['Measurands'].append(self._create_widget(model))

        tree['Real-time plots'] = []

        tree['Experiments'] = []
        for model in self.project.experiments.data:
            tree['Experiments'].append(self._create_widget(model))

        tree['Results'] = []
        tree['Result plots'] = []

        return tree
