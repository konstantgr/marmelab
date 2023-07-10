from ..View import BaseView, QWidgetType
from ...project.PPlots import PRTPlot1D
from PyQt6.QtWidgets import QPushButton, QWidget, QVBoxLayout, QGroupBox, QComboBox, QFormLayout, QLabel
from PyQt6.QtCore import Qt
from typing import Dict, Tuple, Union


class RTPlot1DView(BaseView[PRTPlot1D]):
    def __init__(self, *args, **kwargs):
        super(RTPlot1DView, self).__init__(*args, **kwargs)
        self.selector = QComboBox()
        self.selector_x = QComboBox()
        self.selector_f = QComboBox()
        self.measurands: dict[str: list[str]] = {}

        self.current_measurand_name: str = ''

        self.update_measurands()
        self.model.signals.measurands_changed.connect(self.update_measurands)
        self.model.signals.current_measurand_changed.connect(self.update_measurands)
        self.selector.currentTextChanged.connect(self.set_measurand)

    def construct_widget(self) -> QWidgetType:
        widget = QWidget()
        vbox = QVBoxLayout(widget)
        vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        widget.setLayout(vbox)

        group = QGroupBox(widget)
        group_layout = QFormLayout(group)
        group_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        vbox.addWidget(group)

        group_layout.addRow(QLabel('Measurable'), self.selector)
        group_layout.addRow(QLabel('x - axis data'), self.selector_x)
        group_layout.addRow(QLabel('f(x)'), self.selector_f)

        button = QPushButton('Apply')
        group_layout.addRow(button)
        button.clicked.connect(self.apply)

        return widget

    def update_measurands(self):
        measurands = self.model.get_measurands()
        self.measurands = measurands
        current_name = self.current_measurand_name
        self.selector.clear()
        names = list(self.measurands.keys())
        if current_name not in names:
            names = [''] + names
            current_name = ''
            self.current_measurand_name = current_name
        self.selector.addItems(names)
        self.selector.setCurrentIndex(names.index(current_name))
        self.update_data_names()

    def update_data_names(self):
        self.selector_x.clear()
        self.selector_f.clear()
        current_meas_name = self.current_measurand_name
        if current_meas_name in self.measurands:
            names_x = names_f = self.measurands[current_meas_name]
            if current_meas_name == self.model.current_measurand_name:
                x_name = self.model.x_data_name
                f_name = self.model.f_data_name
            else:
                x_name = f_name = ''
            if x_name == '':
                names_x = [''] + names_x
            if f_name == '':
                names_f = [''] + names_f
            self.selector_x.addItems(names_x)
            self.selector_f.addItems(names_f)
            self.selector_x.setCurrentText(x_name)
            self.selector_f.setCurrentText(f_name)

    def set_measurand(self, name: str):
        self.current_measurand_name = name
        self.update_data_names()

    def apply(self):
        self.model.set_settings(
            self.current_measurand_name,
            x_data_name=self.selector_x.currentText(),
            f_data_name=self.selector_f.currentText()
        )
