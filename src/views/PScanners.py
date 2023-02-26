from PyQt6.QtWidgets import QSplitter
from PyQt6.QtWidgets import QWidget, QSizePolicy, QGroupBox, QVBoxLayout
from .Widgets import SettingsTableWidget, StateDepPushButton
from ..Variable import Setting
from ..project.PScanners import TRIMPScanner
from ..scanner.scanner import Position
from PyQt6.QtCore import Qt, QThreadPool
from .View import BaseView, QWidgetType


import logging
logger = logging.getLogger()


class TRIMControl(BaseView[TRIMPScanner]):
    def __init__(self, *args, **kwargs):
        super(TRIMControl, self).__init__(*args, **kwargs)
        states = self.model.states

        self.connect_button = StateDepPushButton(
            state=~states.is_connected & ~states.is_in_use,
            text="Connect",
        )

        m_state = states.is_connected & ~states.is_moving & ~states.is_in_use
        self.disconnect_button = StateDepPushButton(
            state=m_state,
            text="Disconnect",
        )
        self.home_button = StateDepPushButton(
            state=m_state,
            text="Home",
        )
        self.abort_button = StateDepPushButton(
            state=states.is_connected,
            text="Abort",
        )

    def construct_widget(self) -> QWidgetType:
        widget = QWidget()
        vbox = QVBoxLayout(widget)
        vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        widget.setLayout(vbox)

        widget._thread_pool = QThreadPool()

        group = QGroupBox(widget)
        group_layout = QVBoxLayout(group)
        group_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        vbox.addWidget(group)

        self.connect_button.clicked.connect(self.model.instrument.connect)
        self.disconnect_button.clicked.connect(self.model.instrument.disconnect)
        self.home_button.clicked.connect(self.f_home)
        self.abort_button.clicked.connect(self.model.instrument.abort)

        self.abort_button.setProperty('color', 'red')
        group_layout.addWidget(self.connect_button)
        group_layout.addWidget(self.disconnect_button)
        group_layout.addWidget(self.home_button)
        group_layout.addWidget(self.abort_button)

        return widget

    def _home(self):
        self.model.instrument.home()
        self.model.instrument.set_settings(position=Position(2262.92, 2137.09, 0, 0))
        logger.debug("Scanner at home. Scanner position is:")
        current_position = self.model.instrument.position()
        logger.debug(f'x: {current_position.x}')
        logger.debug(f'y: {current_position.y}')
        logger.debug(f'z: {current_position.z}')
        logger.debug(f'w: {current_position.z}')

    def f_home(self):
        """
        This function sets "home" current cords.
        """
        # self._thread_pool.start(Worker(self._home))
        self._home()

    def display_name(self) -> str:
        return "Control"


class TRIMSettings(BaseView[TRIMPScanner]):
    def __init__(self, *args, **kwargs):
        super(TRIMSettings, self).__init__(*args, **kwargs)
        self.signals = self.model.signals
        self.states = self.model.states

        self.settings_table = SettingsTableWidget(
            settings=self.model.get_settings(),
            apply_state=self.states.is_connected & ~self.states.is_moving & ~self.states.is_in_use,
            apply=self.apply
        )

    def construct_widget(self) -> QWidgetType:
        widget = QWidget()
        widget.setLayout(QVBoxLayout())
        splitter = QSplitter(orientation=Qt.Orientation.Vertical)
        widget.layout().addWidget(splitter)
        widget.layout().setContentsMargins(0, 0, 0, 0)

        splitter.addWidget(self.settings_table)
        splitter.addWidget(QWidget())
        splitter.setChildrenCollapsible(False)
        splitter.setProperty('type', 'inner')
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        return widget

    def apply(self):
        self.model.set_settings(**self.settings_table.table.to_dict())
        logger.info("Settings were applied")

    def display_name(self) -> str:
        return "Settings"
