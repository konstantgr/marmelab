from ..Project import PScanner, PWidget, PScannerSignals
from PyQt6.QtWidgets import QWidget, QTextEdit
from ..Widgets import SettingsTableWidget
from ..Variable import Setting, Unit
from ...scanner.TRIM import TRIMScanner, DEFAULT_SETTINGS
from ..icons import settings_icon, control_icon


class Control(QTextEdit):
    def __init__(self, signals: PScannerSignals):
        super().__init__()
        self.setText('Scanner Control')


class Settings(SettingsTableWidget):
    def __init__(self, signals: PScannerSignals, settings: list[Setting], parent: QWidget = None):
        super(Settings, self).__init__(settings=settings, parent=parent)
        self.signals = signals

    def apply(self):
        self.signals.set_settings.emit(self.table.to_dict())


class TRIMPScanner(PScanner):
    def __init__(self, *args, instrument: TRIMScanner, **kwargs):
        super(TRIMPScanner, self).__init__(*args, instrument, **kwargs)

        self._control_widgets = [
            PWidget(
                'Control',
                Control(self.signals),
                icon=control_icon
            ),
            PWidget(
                'Settings',
                Settings(self.signals, settings=self._get_settings()),
                icon=settings_icon
            )
        ]

    @property
    def control_widgets(self) -> list[PWidget]:
        return self._control_widgets

    def _get_settings(self) -> list[Setting]:
        res = []
        UNITS = {
            'acceleration': Unit(m=1, s=-2),
            'deceleration': Unit(m=1, s=-2),
            'velocity': Unit(m=1, s=-1),
        }
        TYPES = {
            'motion_mode': int,
            'special_motion_mode': int,
            'motor_on': int
        }
        for key, value in DEFAULT_SETTINGS.items():
            for axis_name, axis_value in value.__dict__.items():
                var_name = f"{key}_{axis_name}"
                res.append(Setting(
                    name=var_name,
                    unit=unit if (unit := UNITS.get(key)) is not None else Unit(),
                    description='',
                    type=type_ if (type_ := TYPES.get(key)) is not None else float,
                    default_value=axis_value,
                ))
        return res
