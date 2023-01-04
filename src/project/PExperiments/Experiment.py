import numpy as np
import pandas as pd

from ..Project import (
    PExperiment, PPath, PMeasurable, PScanner, PAnalyzer,
    PScannerStates, PAnalyzerStates,
)
from ..Widgets import StateDepPushButton
from ...scanner import Position
from PyQt6.QtWidgets import QTextEdit, QWidget, QVBoxLayout, QGroupBox, QSizePolicy
from PyQt6.QtCore import Qt, QThreadPool
from typing import Callable


class Control(QWidget):
    def __init__(
            self,
            analyzer_states: PAnalyzerStates,
            scanner_states: PScannerStates,
            experiment_func: Callable
    ):
        super(Control, self).__init__()
        vbox = QVBoxLayout(self)
        vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(vbox)

        self._thread_pool = QThreadPool()

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

        self.connect_button.clicked.connect(experiment_func)
        group_layout.addWidget(self.connect_button)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)


class Experiment(PExperiment):
    def __init__(
            self,
            name: str,
            p_analyzer: PAnalyzer,
            p_scanner: PScanner,
            p_path: PPath,
            p_measurement: PMeasurable,
            output_file: str
    ):
        super(Experiment, self).__init__(
            name=name,
            widget=Control(p_analyzer.states, p_scanner.states, self.run)
        )

        self.scanner = p_scanner
        self.analyzer = p_analyzer
        self.measurable = p_measurement

        self.path = p_path
        self.output_file = output_file

    def run(self):
        self.scanner.states.is_in_use.set(True)
        self.analyzer.states.is_in_use.set(True)

        for idx, pos in enumerate(self.path.get_points()):
            self.scanner.instrument.goto(pos)

            res_dict = self.measurable.measure()
            res_df = pd.DataFrame(res_dict)
            res_df.to_csv(self.output_file, mode='a', header=False)

        self.scanner.states.is_in_use.set(False)
        self.analyzer.states.is_in_use.set(False)

    def create_data(self):
        parameters_names = list(self.measurable.measure().keys())
        dimensions_num = ['x', 'y', 'z', 'w']

        header = [*parameters_names, *dimensions_num]
        pd.DataFrame(columns=header).to_csv(self.output_file)


if __name__ == "__main__":

    # experiment = Experiment(analyzer, scanner, params, route, 'data/exp1/test.csv')
    # experiment.run()

    print(2)
