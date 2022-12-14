from ..Project import PAnalyzer, PWidget, PAnalyzerSignals
from PyQt6.QtWidgets import QWidget, QTextEdit, QPushButton, QVBoxLayout, QSizePolicy
from ..icons import control_icon
from PyQt6.QtCore import Qt


class Control(QWidget):
    def __init__(self, signals: PAnalyzerSignals):
        super(Control, self).__init__()
        super().__init__()
        vbox = QVBoxLayout(self)
        self.connect_button = QPushButton("Connect")
        self.connect_button.setFixedSize(100, 50)

        vbox.addWidget(self.connect_button)
        vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(vbox)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)


class Settings(QTextEdit):
    def __init__(self, signals: PAnalyzerSignals):
        super(Settings, self).__init__()
        self.setText('Analyzer Settings')


class RohdeSchwarzPAnalyzer(PAnalyzer):
    def __init__(self, *args, **kwargs):
        super(RohdeSchwarzPAnalyzer, self).__init__(*args, **kwargs)

        self._control_widgets = [
            PWidget(
                'Control',
                Control(self.signals),
                icon=control_icon
            ),
            # PWidget(
            #     'Settings',
            #     Settings(self.signals)
            # )
        ]

    @property
    def control_widgets(self) -> list[PWidget]:
        return self._control_widgets
