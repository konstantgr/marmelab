from PyQt6.QtWidgets import QWidget, QGroupBox, QVBoxLayout, QCheckBox, QFormLayout, \
    QLineEdit, QComboBox, QGridLayout, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIntValidator, QDoubleValidator
from src.views.View import BaseView, QWidgetType
from src.project.PAnalyzers.ceyear import SParams, CEYEAR_DEFAULT_SETTINGS
from src.views.Widgets import StateDepPushButton
from functools import partial


class SParamsView(BaseView[SParams]):
    def __init__(self, *args, **kwargs):
        super(SParamsView, self).__init__(*args, **kwargs)
        self.settings_to_apply = CEYEAR_DEFAULT_SETTINGS.copy()

    def construct_widget(self) -> QWidgetType:
        widget = QWidget()
        vbox = QVBoxLayout(widget)
        vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        widget.setLayout(vbox)

        group = self._construct_sparams_widget(widget)
        freq_form = self._construct_frequency_widget(widget)
        smoothing_form = self._construct_smoothing_widget(widget)
        bandwidth_form = self._construct_bandwidth_widget(widget)
        averaging_form = self._construct_averaging_widget(widget)
        power_form = self._construct_power_widget(widget)
        sweep_form = self._construct_sweep_type_widget(widget)
        apply_button = self._construct_apply_button(widget)

        vbox.addWidget(group)
        vbox.addWidget(sweep_form)
        vbox.addWidget(freq_form)
        vbox.addWidget(bandwidth_form)
        vbox.addWidget(power_form)
        vbox.addWidget(smoothing_form)
        vbox.addWidget(averaging_form)
        vbox.addWidget(apply_button)
        return widget

    def _construct_apply_button(self, parent_widget):
        # apply_button = QPushButton(parent_widget)
        apply_button = StateDepPushButton(
            state=self.model.panalyzer.states.is_connected & ~self.model.panalyzer.states.is_in_use,
            text="Apply",
            parent=parent_widget
        )
        apply_button.setText("Apply")
        apply_button.clicked.connect(self.model.pre_measure)
        return apply_button

    def _construct_sparams_widget(self, parent_widget):
        def change_sparam(s_param):
            s_param.enable = not s_param.enable
        group = QGroupBox(parent_widget)
        group_layout = QGridLayout(group)
        for s_param in self.model.s_params:
            s_param_cb = QCheckBox(s_param.name, group)
            group_layout.addWidget(s_param_cb)
            s_param_cb.stateChanged.connect(lambda: change_sparam(s_param))
        return group

    def _construct_sweep_type_widget(self, parent_widget):
        sweep_form = QWidget(parent_widget)
        sweep_form_layout = QFormLayout(parent_widget)
        sweep_box = QComboBox(sweep_form)
        sweep_box.addItems(["LIN", "LOG"])
        sweep_form_layout.addRow("Sweep type", sweep_box)
        sweep_box.activated.connect(lambda: self.model.set_sweep_type(sweep_box.currentText()))
        sweep_form.setLayout(sweep_form_layout)
        return sweep_form

    def _construct_frequency_widget(self, parent_widget):
        freq_form = QWidget(parent_widget)
        freq_form_layout = QFormLayout(parent_widget)
        freq_start_le = QLineEdit(f"{CEYEAR_DEFAULT_SETTINGS['freq_start']}", freq_form)
        freq_stop_le = QLineEdit(f"{CEYEAR_DEFAULT_SETTINGS['freq_stop']}", freq_form)
        freq_points_le = QLineEdit(f"{CEYEAR_DEFAULT_SETTINGS['freq_num']}", freq_form)
        freq_start_le.setValidator(QDoubleValidator())
        freq_stop_le.setValidator(QDoubleValidator())
        freq_points_le.setValidator(QIntValidator())
        freq_form_layout.addRow("Start (Hz)", freq_start_le)
        freq_form_layout.addRow("Stop (Hz)", freq_stop_le)
        freq_form_layout.addRow("N points", freq_points_le)
        freq_start_le.editingFinished.connect(lambda: self.model.set_freq_start(float(freq_start_le.text())))
        freq_stop_le.editingFinished.connect(lambda: self.model.set_freq_stop(float(freq_stop_le.text())))
        freq_points_le.editingFinished.connect(lambda: self.model.set_freq_num(int(freq_points_le.text())))
        freq_form.setLayout(freq_form_layout)
        return freq_form

    def _construct_smoothing_widget(self, parent_widget):
        smoothing_form = QWidget(parent_widget)
        smoothing_form_layout = QFormLayout(parent_widget)
        smoothing_le = QLineEdit(f"{CEYEAR_DEFAULT_SETTINGS['smooth_apert']}", smoothing_form)
        smoothing_le.setValidator(QDoubleValidator())  # todo: не вводится число?!?!?!
        smoothing_form_layout.addRow("Smoothing aperture (%)", smoothing_le)
        smoothing_le.editingFinished.connect(lambda: self.model.set_smooth_apert(float(smoothing_le.text())))
        smoothing_form.setLayout(smoothing_form_layout)
        return smoothing_form

    def _construct_bandwidth_widget(self, parent_widget):
        bandwidth_form = QWidget(parent_widget)
        bandwidth_form_layout = QFormLayout(parent_widget)
        bandwidth_box = QComboBox(bandwidth_form)
        bandwidth_box.addItems(map(str, [1, 2, 3, 5, 7, 10, 15, 20, 30, 50, 70, 100, 150, 200, 300, 500, 700, 1000,
                                         1500, 2000, 5000, 7000, 10_000, 15_000, 20_000, 30_000, 35_000, 40_000]))
        bandwidth_form_layout.addRow("Bandwidth (Hz)", bandwidth_box)
        bandwidth_box.activated.connect(lambda: self.model.set_bandwidth(int(bandwidth_box.currentText())))
        bandwidth_form.setLayout(bandwidth_form_layout)
        return bandwidth_form

    def _construct_averaging_widget(self, parent_widget):
        averaging_form = QWidget(parent_widget)
        averaging_form_layout = QFormLayout(parent_widget)
        averaging_le = QLineEdit(f"{CEYEAR_DEFAULT_SETTINGS['aver_fact']}", averaging_form)
        averaging_le.setValidator(QIntValidator())
        averaging_form_layout.addRow("Average factor:", averaging_le)
        averaging_le.editingFinished.connect(lambda: self.model.set_aver_fact(int(averaging_le.text())))
        averaging_form.setLayout(averaging_form_layout)
        return averaging_form

    def _construct_power_widget(self, parent_widget):
        power_form = QWidget(parent_widget)
        power_form_layout = QFormLayout(parent_widget)
        power_le = QLineEdit(f"{CEYEAR_DEFAULT_SETTINGS['power']}", power_form)
        power_le.setValidator(QIntValidator())
        power_form_layout.addRow("Power (dBm)", power_le)
        power_le.editingFinished.connect(lambda: self.model.set_power(int(power_le.text())))
        power_form.setLayout(power_form_layout)
        return power_form

    def display_name(self) -> str:
        return self.model.name