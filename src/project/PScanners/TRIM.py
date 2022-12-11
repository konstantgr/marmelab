from ..Project import PScanner, PWidget, PScannerSignals
from PyQt6.QtWidgets import QWidget, QTextEdit
from ..Widgets import SettingsTableWidget
from ..Variable import Setting, Unit


class Control(QTextEdit):
    def __init__(self, signals: PScannerSignals):
        super().__init__()
        self.setText('Scanner Control')


class Settings(SettingsTableWidget):
    def __init__(self, signals: PScannerSignals, parent: QWidget = None):
        settings = [
            Setting(name='123', unit=Unit(1, -2, 3), description='test', default_value=123)
        ]
        super(Settings, self).__init__(settings=settings, parent=parent)


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
                Settings(self.signals, None)
            )
        ]

    @property
    def control_widgets(self) -> list[PWidget]:
        return self._control_widgets
