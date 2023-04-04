from ..project.PExperiments import Experiment
from .View import BaseView, QWidgetType
from PyQt6.QtWidgets import QWidget, QHeaderView, QHBoxLayout, QTableView, QVBoxLayout, QSizePolicy, QGroupBox, \
    QComboBox, QPushButton
from src.views.Widgets import StateDepPushButton, StateDepCheckBox
from PyQt6.QtCore import Qt


class ExperimentView(BaseView[Experiment]):
    def __init__(self, *args, **kwargs):
        super(ExperimentView, self).__init__(*args, **kwargs)
        self.paths_q_box = QComboBox()

    def upd_paths(self):
        self.paths_q_box.clear()
        self.paths_q_box.addItems(self.model.paths)
        self.paths_q_box.setCurrentText(self.model.current_path)

    def construct_widget(self) -> QWidgetType:
        self.model.signals.path_changed.connect(self.upd_paths)

        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        group = QGroupBox()
        group_layout = QVBoxLayout(group)
        group_layout.addWidget(self.paths_q_box)

        layout.addWidget(group)
        return widget


