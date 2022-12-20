from ..Project import PMeasurable, PMeasurand
from dataclasses import dataclass, field
from PyQt6.QtWidgets import QTextEdit, QWidget, QComboBox
from pyqtgraph import PlotWidget
from typing import Any
from PyQt6.QtWidgets import QVBoxLayout, QStackedWidget


class MeasurableWidget(QWidget):
    def __init__(self, measurable: PMeasurable, measurands: list[PMeasurand]):
        super(MeasurableWidget, self).__init__()
        self.measurable = measurable
        self.measurands = measurands
        self.current_measurand = self.measurands[0]

        self.setLayout(QVBoxLayout())
        self.combo_box = QComboBox()
        self.stacked_widgets = QStackedWidget()
        self.layout().addWidget(self.combo_box)
        self.layout().addWidget(self.stacked_widgets)

        self.combo_box.currentIndexChanged.connect(self.set_current_measurand)

        self.update_measurands()

    def set_current_measurand(self, i):
        self.stacked_widgets.setCurrentIndex(i)
        self.current_measurand = self.measurands[i]

        self.measurable.signals.changed.emit()

    def update_measurands(self):
        self.combo_box.clear()
        for i in range(self.stacked_widgets.count()):
            self.stacked_widgets.removeWidget(self.stacked_widgets.widget(i))

        for measurand in self.measurands:
            self.combo_box.addItem(measurand.name)
            self.stacked_widgets.addWidget(measurand.widget)


@dataclass
class MeasurableOfMeasurands(PMeasurable):
    measurands: list[PMeasurand] = field(default_factory=list)
    widget: MeasurableWidget = None
    _flag: bool = False

    def __post_init__(self):
        self.widget = MeasurableWidget(
            measurable=self,
            measurands=self.measurands
        )
        self.signals.changed.connect(self._set_flag)

    def _set_flag(self):
        self._flag = True

    @property
    def plot_widget(self) -> PlotWidget:
        return self.widget.current_measurand.plot_widget

    def measure(self) -> Any:
        if self._flag:
            self._flag = False
            self.pre_measure()
        return self.widget.current_measurand.measure()

    def pre_measure(self) -> Any:
        return self.widget.current_measurand.pre_measure()
