from src.project import PScanner, PWidget, PScannerSignals
from PyQt6.QtWidgets import QWidget, QTextEdit


class Control(QTextEdit):
    def __init__(self, signals: PScannerSignals):
        super().__init__()
        self.setText('Scanner Control')


class Settings(QTextEdit):
    def __init__(self, signals: PScannerSignals):
        super(Settings, self).__init__('')
        self.setText('Scanner Settings')


class TRIMPScanner(PScanner):
    def __init__(self, *args, **kwargs):
        super(TRIMPScanner, self).__init__(*args, **kwargs)

        self._control_widgets = [
            PWidget(
                'Control',
                Control(self.signals)
            ),
            PWidget(
                'Settings',
                Settings(self.signals)
            )
        ]

    @property
    def control_widgets(self) -> list[PWidget]:
        return self._control_widgets
