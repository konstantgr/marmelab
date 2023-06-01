from ..View import BaseView, QWidgetType
from ...project.PPlots import ResPPlot3DS
from PyQt6.QtWidgets import QPushButton, QWidget, QVBoxLayout, QGroupBox, QComboBox, QFormLayout, QLabel
from PyQt6.QtCore import Qt
from typing import Dict, Tuple, Union


class ResPPlot3DSView(BaseView[ResPPlot3DS]):
    def construct_widget(self) -> QWidgetType:
        widget = QWidget()
        return widget
