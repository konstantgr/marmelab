from ..project.PExperiments import Experiment
from .View import BaseView, QWidgetType
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QGroupBox, QComboBox, QListView, QLabel, QPushButton
from src.views.Widgets import StateDepPushButton, StateDepCheckBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QStandardItem, QStandardItemModel


class ExperimentView(BaseView[Experiment]):
    def __init__(self, *args, **kwargs):
        super(ExperimentView, self).__init__(*args, **kwargs)
        self.paths_q_box = QComboBox()
        self.measurands_item_model = QStandardItemModel()
        self.states = self.model.scanner.states
        self.model.signals.path_changed.connect(self.upd_paths)
        self.paths_q_box.currentTextChanged.connect(self.model.set_current_path)

        self.model.signals.measurands_changed.connect(self.upd_measurands)
        self.measurands_item_model.itemChanged.connect(self.parse_checked_fields)

    def upd_paths(self):
        current_path = self.model.current_path
        lst_paths = self.model.paths
        self.paths_q_box.clear()
        if current_path == '':
            lst_paths = [''] + lst_paths
        self.paths_q_box.addItems(lst_paths)
        print(current_path)
        self.paths_q_box.setCurrentIndex(lst_paths.index(current_path))

    def upd_measurands(self):
        current_measurands = self.model.current_measurands
        lst_measurands = self.model.measurands
        self.measurands_item_model.clear()
        for string in lst_measurands:
            item = QStandardItem(string)
            item.setCheckable(True)
            if string in current_measurands:
                check = Qt.CheckState.Checked
            else:
                check = Qt.CheckState.Unchecked
            item.setCheckState(check)
            self.measurands_item_model.appendRow(item)

    def parse_checked_fields(self, item):
        lst_checked = []
        for i in range(self.measurands_item_model.rowCount()):
            if (a := self.measurands_item_model.item(i, 0)).checkState() == Qt.CheckState.Checked:
                lst_checked.append(a.text())
        print(lst_checked)
        self.model.set_current_measurands(lst_checked)

    def construct_widget(self) -> QWidgetType:

        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        group = QGroupBox()
        group_layout = QVBoxLayout(group)
        group_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        group_layout.addWidget(QLabel('Path:'))
        group_layout.addWidget(self.paths_q_box)

        list_view = QListView()
        list_view.setModel(self.measurands_item_model)
        list_view.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        group_layout.addWidget(QLabel('Measurands:'))

        go_button = StateDepPushButton(
            state=self.states.is_connected,
            text="Run experiment",
            parent=widget
        )

        go_button.clicked.connect(self.model.run_push)
        group_layout.addWidget(list_view)
        group_layout.addWidget(go_button)

        layout.addWidget(group)
        self.upd_paths()
        self.upd_measurands()
        return widget


