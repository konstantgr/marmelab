from ..View import BaseView, QWidgetType
from ...project.PPlots import PRTPlot1D
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QComboBox, QFormLayout, QLabel
from PyQt6.QtCore import Qt
from typing import  Dict, Tuple, Union


class RTPlot1DView(BaseView[PRTPlot1D]):
    def __init__(self, *args, **kwargs):
        super(RTPlot1DView, self).__init__(*args, **kwargs)
        self.selector = QComboBox()
        self.selector_x = QComboBox()
        self.selector_f = QComboBox()
        self.measurands: Dict[str, Tuple[str], ...] = {}

        self.current_measurand: Union[str, None] = None

        self.update_measurands()
        self.model.signals.measurands_changed.connect(self.update_measurands)

        self.selector.currentTextChanged.connect(self.set_measurand)
        self.selector_x.currentTextChanged.connect(self.set_x)
        self.selector_f.currentTextChanged.connect(self.set_f)

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
        group_layout.addRow(QLabel('x'), self.selector_x)
        group_layout.addRow(QLabel('f'), self.selector_f)

        return widget

    def update_measurands(self):
        measurands = self.model.get_measurands()
        self.measurands = {}
        for measurand in measurands:
            self.measurands[measurand.name] = measurand.get_measure_names()

        cur_i = self.selector.currentIndex()
        self.selector.clear()
        self.selector.addItems(self.measurands.keys())
        # if cur_i >= len(self.measurands.keys()):
        #     self.selector.setCurrentIndex(len(self.measurands.keys())-1)
        # else:
        #     self.selector.setCurrentIndex(cur_i)

    def set_measurand(self, name: str):
        print(name)

    def set_f(self, name: str):
        self.model.set_f_data_name(name)

    def set_x(self, name: str):
        self.model.set_x_data_name(name)
