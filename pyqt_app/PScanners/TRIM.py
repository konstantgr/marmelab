from src.project import PScanner, PWidget, PScannerSignals
from src.scanner.TRIM import TRIMScanner
from PyQt6.QtWidgets import QWidget, QTextEdit


class Control(QTextEdit):
    def __init__(self, signals: PScannerSignals):
        super(Control, self).__init__()
        self.setText('Scanner Control')


class Settings(QTextEdit):
    def __init__(self, signals: PScannerSignals):
        super(Settings, self).__init__()
        self.setText('Scanner Settings')


class TRIMPScanner(PScanner):
    def __init__(
            self,
            signals: PScannerSignals,
            instrument: TRIMScanner,
    ):
        super(TRIMPScanner, self).__init__(
            signals=signals,
            instrument=instrument
        )

        self._control_widgets = [
            PWidget(
                'Control',
                Control(signals)
            ),
            PWidget(
                'Settings',
                Settings(signals)
            )
        ]

    def control_widgets(self) -> list[PWidget]:
        return self._control_widgets
