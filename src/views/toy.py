from PyQt6.QtWidgets import QLabel, QTextEdit, QHBoxLayout
from .View import BaseView, QWidgetType


class ToyView(BaseView):
    def construct_widget(self) -> QWidgetType:
        widget = QTextEdit(f'{self.model.name} {self.display_name()}')
        return widget


class ToyScannerControl(ToyView):
    def display_name(self) -> str:
        return 'Control'


class ToyScannerSettings(ToyView):
    def display_name(self) -> str:
        return 'Settings'

