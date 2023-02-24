from PyQt6.QtWidgets import QLabel, QTextEdit, QHBoxLayout
from .View import BaseView


class ToyView(BaseView):
    def __init__(self, model, *args, **kwargs):
        super(ToyView, self).__init__(model=model, *args, **kwargs)
        layout = QHBoxLayout()
        self.setLayout(layout)
        widget = QTextEdit(f'{model.name} {self.display_name()}')
        layout.addWidget(widget)


class ToyScannerControl(ToyView):
    def display_name(self) -> str:
        return 'Control'


class ToyScannerSettings(ToyView):
    def display_name(self) -> str:
        return 'Settings'

