from PyQt6.QtWidgets import QWidget, QVBoxLayout, QFormLayout, QComboBox
from PyQt6.QtCore import Qt
from src.views.View import BaseView, QWidgetType
from src.project.PMeasurands.time_measurand import TimeMeas
from functools import partial


class TimeView(BaseView[TimeMeas]):
    def __init__(self, *args, **kwargs):
        super(TimeView, self).__init__(*args, **kwargs)

    def construct_widget(self) -> QWidgetType:
        widget = QWidget()
        vbox = QVBoxLayout(widget)
        vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        widget.setLayout(vbox)

        sweep_form = self._construct_time_format_widget(widget)

        vbox.addWidget(sweep_form)
        return widget

    def _construct_time_format_widget(self, parent_widget):
        form = QWidget(parent_widget)
        form_layout = QFormLayout(parent_widget)
        box = QComboBox(form)
        box.addItems(["YYYY-MM-DD H:M:S", "MM-DD H:M:S", "H:M:S", "unix"])
        form_layout.addRow("Time format", box)
        slot = partial(self.model.set_time_format, box.currentText())
        box.activated.connect(slot)
        form.setLayout(form_layout)
        return form

    def display_name(self) -> str:
        return self.model.name