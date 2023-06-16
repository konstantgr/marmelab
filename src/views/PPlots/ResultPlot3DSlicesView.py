from ..View import BaseView, QWidgetType
from ...project.PPlots import ResPPlot3DS
from PyQt6.QtWidgets import QPushButton, QWidget, QVBoxLayout, QGroupBox, QComboBox, QFormLayout, QLabel
from PyQt6.QtCore import Qt

from typing import Dict, Tuple, Union


class ResPPlot3DSView(BaseView[ResPPlot3DS]):
    def __init__(self, *args, **kwargs):
        super(ResPPlot3DSView, self).__init__(*args, **kwargs)
        self.selector = QComboBox()
        self.selector_x = QComboBox()
        self.selector_y = QComboBox()
        self.selector_f = QComboBox()
        self.selector.textHighlighted.connect(self.update_results)
        self.results = {}

    def construct_widget(self) -> QWidgetType:
        widget = QWidget()
        vbox = QVBoxLayout(widget)
        vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        widget.setLayout(vbox)

        group = QGroupBox(widget)
        group_layout = QFormLayout(group)
        group_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        vbox.addWidget(group)

        group_layout.addRow(QLabel('Result'), self.selector)
        group_layout.addRow(QLabel('x - axis data'), self.selector_x)
        group_layout.addRow(QLabel('y - axis data'), self.selector_y)
        group_layout.addRow(QLabel('f(x, y)'), self.selector_f)

        button = QPushButton('Apply')
        group_layout.addRow(button)
        button.clicked.connect(self.apply)
        self.update_results()
        return widget

    def update_results(self, *args):

        results = self.model.get_results()
        self.results = results
        self.selector.clear()
        names = ['DOESN`T WORK'] + list(self.results.keys())
        self.selector.addItems(names)
        self.update_data_names()

    def update_data_names(self):
        self.selector_x.clear()
        self.selector_y.clear()
        self.selector_f.clear()

        current_res_name = self.selector.currentText()
        if current_res_name in self.results:
            names_x = names_y = names_f = [''] + self.results[current_res_name]
        else:
            names_x = names_y = names_f = ['']

        self.selector_x.addItems(names_x)
        self.selector_y.addItems(names_y)
        self.selector_f.addItems(names_f)

    def set_measurand(self, name: str):
        self.current_measurand_name = name
        self.update_data_names()

    def apply(self):
        self.model.set_settings(
            self.current_measurand_name,
            x_data_name=self.selector_x.currentText(),
            f_data_name=self.selector_f.currentText()
        )
