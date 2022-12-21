from ..Project import PScanner, PWidget, PScannerSignals, PScannerStates
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QGroupBox, QSplitter
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QGroupBox
from ..Widgets import SettingsTableWidget, StateDepPushButton
from ..Variable import Setting, Unit
from ...scanner.TRIM import TRIMScanner, DEFAULT_SETTINGS
from ...scanner.scanner import Position
from ..icons import settings_icon, control_icon
from ..Worker import Worker
from PyQt6.QtCore import Qt, QThreadPool


import logging
logger = logging.getLogger()


class Control(QWidget):
    def __init__(self, states: PScannerStates, scanner: TRIMScanner):
        super().__init__()
        self.scanner = scanner
        vbox = QVBoxLayout(self)
        vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(vbox)

        self._thread_pool = QThreadPool()

        group = QGroupBox(self)
        group_layout = QVBoxLayout(group)
        group_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        vbox.addWidget(group)

        self.connect_button = StateDepPushButton(
            state=~states.is_connected & ~states.is_in_use,
            text="Connect",
            parent=self
        )
        m_state = states.is_connected & ~states.is_moving & ~states.is_in_use
        self.disconnect_button = StateDepPushButton(
            state=m_state,
            text="Disconnect",
            parent=self
        )
        self.home_button = StateDepPushButton(
            state=m_state,
            text="Home",
            parent=self
        )
        self.abort_button = StateDepPushButton(
            state=states.is_connected,
            text="Abort",
            parent=self
        )

        self.connect_button.clicked.connect(scanner.connect)
        self.disconnect_button.clicked.connect(scanner.disconnect)
        self.home_button.clicked.connect(self.f_home)
        self.abort_button.clicked.connect(scanner.abort)

        self.abort_button.setProperty('color', 'red')
        group_layout.addWidget(self.connect_button)
        group_layout.addWidget(self.disconnect_button)
        group_layout.addWidget(self.home_button)
        group_layout.addWidget(self.abort_button)

        #self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)

    def _home(self):
        self.scanner.home()
        self.scanner.set_settings(position=Position(2262.92, 2137.09, 0, 0))
        logger.debug("Scanner at home. Scanner position is:")
        current_position = self.scanner.position()
        logger.debug(f'x: {current_position.x}')
        logger.debug(f'y: {current_position.y}')
        logger.debug(f'z: {current_position.z}')
        logger.debug(f'w: {current_position.z}')

    def f_home(self):
        """
        This function sets "home" current cords.
        """
        self._thread_pool.start(Worker(self._home))

    def f_upd_cur_pos(self):
        logger.debug("Scanner position is:")
        current_position = self.scanner.position()
        logger.debug('x: ', current_position.x)
        logger.debug('y: ', current_position.y)
        logger.debug('z: ', current_position.z)


class Settings(QSplitter):
    def __init__(
            self,
            signals: PScannerSignals,
            states: PScannerStates,
            settings: list[Setting],
            parent: QWidget = None
    ):
        super(Settings, self).__init__(
            parent=parent,
            orientation=Qt.Orientation.Vertical,
        )
        self.signals = signals

        self.settings_table = SettingsTableWidget(
            settings=settings,
            parent=self,
            apply_state=states.is_connected & ~states.is_moving & ~states.is_in_use
        )
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.addWidget(self.settings_table)
        self.addWidget(QWidget())
        self.setChildrenCollapsible(False)
        self.setProperty('type', 'inner')

    def apply(self):
        self.signals.set_settings.emit(self.settings_table.table.to_dict())


class TRIMPScanner(PScanner):
    def __init__(self, *args, instrument: TRIMScanner, **kwargs):
        super(TRIMPScanner, self).__init__(*args, instrument, **kwargs)

        self._control_widgets = [
            PWidget(
                'Control',
                Control(self.states, instrument),
                icon=control_icon
            ),
            PWidget(
                'Settings',
                Settings(
                    signals=self.signals,
                    states=self.states,
                    settings=self._get_settings()),
                icon=settings_icon
            )
        ]

    @property
    def control_widgets(self) -> list[PWidget]:
        return self._control_widgets

    @staticmethod
    def _get_settings() -> list[Setting]:
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
