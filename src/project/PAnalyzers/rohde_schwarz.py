from ..Project import PAnalyzer, PWidget, PAnalyzerSignals
from PyQt6.QtWidgets import QWidget, QTextEdit
from ..icons import control_icon


class Control(QTextEdit):
    def __init__(self, signals: PAnalyzerSignals):
        super(Control, self).__init__()
        self.setText('Analyzer Control')


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
