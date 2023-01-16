import dataclasses

import pandas as pd

from ..Project import (
    PExperiment, PPath, PMeasurable, PScanner, PAnalyzer, PBaseSignals, PStorage,
    PScannerStates, PAnalyzerStates,
)
from src.views.Widgets import StateDepPushButton
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QSizePolicy, QComboBox, QLineEdit
from PyQt6.QtCore import Qt, QThreadPool
from typing import Callable


# TODO нужен виджет для эксперимента с выбором measurable и path, и файла, куда сохранять
class Control(QWidget):
    def __init__(
            self,
            analyzer_states: PAnalyzerStates,
            scanner_states: PScannerStates,
            measurables: PStorage[PMeasurable],
            paths: PStorage[PPath],
            experiment_func: Callable
    ):
        super(Control, self).__init__()
        self.measurables = measurables
        self.current_measurable = measurables.data[0]

        self.paths = paths
        self.current_path = paths.data[0]

        vbox = QVBoxLayout(self)
        vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(vbox)

        self._thread_pool = QThreadPool()
        self.input_text = QLineEdit()
        vbox.addWidget(self.input_text)

        self.combo_measurable = QComboBox()
        self.combo_measurable.addItems([i.name for i in self.measurables.data])
        vbox.addWidget(self.combo_measurable)
        self.combo_measurable.currentIndexChanged.connect(self.set_current_measurable)

        self.combo_path = QComboBox()
        self.combo_path.addItems([i.name for i in self.paths.data])
        vbox.addWidget(self.combo_path)
        self.combo_path.currentIndexChanged.connect(self.set_current_path)

        group = QGroupBox(self)
        group_layout = QVBoxLayout(group)
        group_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        vbox.addWidget(group)

        a_state = analyzer_states.is_connected & ~analyzer_states.is_in_use
        b_state = scanner_states.is_connected & ~scanner_states.is_in_use

        self.connect_button = StateDepPushButton(
            state=a_state & b_state,
            text="Run",
            parent=self
        )
        group_layout.addWidget(self.connect_button)
        self.connect_button.clicked.connect(experiment_func)
        group_layout.addWidget(self.connect_button)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)

    def set_current_measurable(self, i):
        self.current_measurable = self.measurables[i]
        self.measurables.signals.changed.emit()

    def set_current_path(self, i):
        self.current_path = self.paths[i]
        self.paths.signals.changed.emit()


class Experiment(PExperiment):
    def __init__(
            self,
            name: str,
            p_analyzer: PAnalyzer,
            p_scanner: PScanner,
            p_paths: PStorage[PPath],
            p_measurements: PStorage[PMeasurable],
    ):
        widget = Control(p_analyzer.states, p_scanner.states, p_measurements, p_paths, self.run)
        super(Experiment, self).__init__(
            name=name,
            widget=widget
        )
        self.widget = widget
        self.signals = PBaseSignals()

        self.scanner = p_scanner
        self.analyzer = p_analyzer
        self.measurables = p_measurements.data[0]

        self.paths = p_paths.data[0]
        self.output_file = None

    def run(self):
        self.scanner.states.is_in_use.set(True)
        self.analyzer.states.is_in_use.set(True)
        # self.widget.current_measurable.pre_measure()

        self.create_data()

        for idx, pos in enumerate(self.widget.current_path.get_points()):
            self.scanner.instrument.goto(pos)

            res_dict = self.widget.current_measurable.measure()
            res_df = pd.DataFrame(res_dict)
            for field in dataclasses.fields(pos):
                if (c := pos.__getattribute__(field.name)) is not None:
                    res_df[field.name] = c
            res_df.to_csv(self.output_file, mode='a', header=False)

        self.scanner.states.is_in_use.set(False)
        self.analyzer.states.is_in_use.set(False)

    def create_data(self):
        self.output_file = self.widget.input_text.text() if self.widget.input_text.text() else 'test.csv'
        print('here', self.output_file)
        parameters_names = list(self.measurables.measure().keys())
        dimensions_num = ['x', 'y', 'z', 'w']

        header = [*parameters_names, *dimensions_num]
        pd.DataFrame(columns=header).to_csv(self.output_file)


if __name__ == "__main__":

    # experiment = Experiment(analyzer, scanner, params, route, 'data/exp1/test.csv')
    # experiment.run()

    print(2)
