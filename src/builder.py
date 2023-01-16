"""
Реализация билдера приложения
"""

from .project import Project
from .project.PScanners import TRIMPScanner
from .views.PScanners import TRIMControl, TRIMSettings

BINDS = {
    TRIMPScanner:
}


class AppBuilder:
    def __init__(
            self,
            project: Project
    ):
        self.project = project

    def tree(self) -> dict[str: list[PWidget]]:
        """
        Дерево проекта
        """
        tree = dict()

        scanner_widgets = []
        for widget in self.scanner.control_widgets:
            scanner_widgets.append(widget)
        tree['Scanner'] = scanner_widgets

        analyzer_widgets = []
        for widget in self.analyzer.control_widgets:
            analyzer_widgets.append(widget)
        tree['Analyzer'] = analyzer_widgets

        tree['Scanner graphics'] = self.scanner_visualizer.control_widgets
        tree['Analyzer graphics'] = self.analyzer_visualizer.control_widgets

        tree['Objects'] = [PWidget(name=w.name, widget=w.widget, icon=w.icon) for w in self.objects.data]
        tree['Paths'] = [PWidget(name=w.name, widget=w.widget, icon=w.icon) for w in self.paths.data]
        tree['Measurables'] = [PWidget(name=w.name, widget=w.widget, icon=w.icon) for w in self.measurables.data]
        tree['Experiments'] = [PWidget(name=w.name, widget=w.widget, icon=w.icon) for w in self.experiments.data]

        return tree
