from ..Project import PScanner, PWidget, PScannerSignals
from PyQt6.QtWidgets import QWidget, QPushButton, QVBoxLayout, QSizePolicy
from ..Widgets import SettingsTableWidget
from ..Variable import Setting, Unit
from ...scanner.TRIM import TRIMScanner, DEFAULT_SETTINGS
from ..icons import settings_icon, control_icon
from PyQt6.QtCore import Qt
from pyqt_app import logger
from src.scanner.TRIM.TRIM_emulator import run  # use it only for emulating


class Control(QWidget):
    def __init__(self, signals: PScannerSignals, scanner: TRIMScanner):
        super().__init__()
        self.scanner = scanner
        vbox = QVBoxLayout(self)
        self.connect_button = QPushButton("Connect")
        self.home_button = QPushButton("Home")
        self.upd_position_button = QPushButton("Update \n current position")
        self.abort_button = QPushButton("Abort")
        self.connect_button.setFixedSize(100, 50)
        self.home_button.setFixedSize(100, 50)
        self.abort_button.setFixedSize(100, 50)
        self.upd_position_button.setFixedSize(100, 75)

        self.connect_button.clicked.connect(self.f_connection)
        self.home_button.clicked.connect(self.f_home)
        self.upd_position_button.clicked.connect(self.f_upd_cur_pos)

        self.abort_button.setStyleSheet("background-color: red")
        vbox.addWidget(self.connect_button)
        vbox.addWidget(self.home_button)
        vbox.addWidget(self.upd_position_button)
        vbox.addWidget(self.abort_button)
        vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(vbox)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)

    def f_connection(self):
        """
        This function makes connection to the scanner
        """
        run(blocking=False, motion_time=2)  # use it only for emulating
        self.scanner.connect()
        logger.info('Scanner is connected')

    def f_home(self):
        """
        This function sets "home" current cords.
        """
        from src.scanner import Position
        self.scanner.home()
        self.scanner.set_settings(position=Position(0, 0, 0, 0))
        logger.debug("Scanner at home. Scanner position is:")
        current_position = self.scanner.position()
        logger.debug('x: ', current_position.x)
        logger.debug('y: ', current_position.y)
        logger.debug('z: ', current_position.z)

    def f_upd_cur_pos(self):
        logger.debug("Scanner position is:")
        current_position = self.scanner.position()
        logger.debug('x: ', current_position.x)
        logger.debug('y: ', current_position.y)
        logger.debug('z: ', current_position.z)


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
                Control(self.signals, instrument),
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
