from PyQt6.QtWidgets import QSplitter
from PyQt6.QtWidgets import QWidget, QSizePolicy, QLineEdit, QGroupBox, QLabel, QVBoxLayout, QFormLayout
from .Widgets import SettingsTableWidget, StateDepPushButton
from ..Variable import Setting
from ..project.PScanners import TRIMPScanner
from ..scanner.scanner import Position
from PyQt6.QtCore import Qt, QThreadPool
from .View import BaseView, QWidgetType
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator

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

        reg_ex = QRegularExpression("[+-]?([0-9]*[.])?[0-9]+")
        self.x_text = QLineEdit()
        self.x_text.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.x_text.setValidator(QRegularExpressionValidator(reg_ex))
        self.y_text = QLineEdit()
        self.y_text.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.y_text.setValidator(QRegularExpressionValidator(reg_ex))
        self.z_text = QLineEdit()
        self.z_text.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.z_text.setValidator(QRegularExpressionValidator(reg_ex))
        self.w_text = QLineEdit()
        self.w_text.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        self.w_text.setValidator(QRegularExpressionValidator(reg_ex))
        self.goto_button = StateDepPushButton(
            state=states.is_connected & ~states.is_in_use,
            text="Go",
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
        self.home_button.clicked.connect(self._home)
        self.abort_button.clicked.connect(self.model.instrument.abort)

        self.abort_button.setProperty('color', 'red')
        group_layout.addWidget(self.connect_button)
        group_layout.addWidget(self.disconnect_button)
        group_layout.addWidget(self.home_button)
        group_layout.addWidget(self.abort_button)

        group_control = QGroupBox(widget)
        group_control_layout = QFormLayout(group_control)
        group_control_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        vbox.addWidget(group_control)

        group_control_layout.addRow(QLabel("x, mm:"), self.x_text)
        group_control_layout.addRow(QLabel("y, mm:"), self.y_text)
        group_control_layout.addRow(QLabel("z, mm:"), self.z_text)
        group_control_layout.addRow(QLabel("w, mm:"), self.w_text)

        buttons_widget = QWidget()
        buttons_widget.setLayout(QVBoxLayout())
        group_control_layout.addRow(buttons_widget)
        buttons_widget.layout().addWidget(self.goto_button)
        self.goto_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        buttons_widget.layout().setAlignment(Qt.AlignmentFlag.AlignRight)
        self.goto_button.clicked.connect(self.goto)
        return widget

    def goto(self):
        x = float(self.x_text.text()) if self.x_text.text().strip() != '' else None
        y = float(self.y_text.text()) if self.y_text.text().strip() != '' else None
        z = float(self.z_text.text()) if self.z_text.text().strip() != '' else None
        w = float(self.w_text.text()) if self.w_text.text().strip() != '' else None
        new_pos = Position(x, y, z, w)
        self.model.instrument.goto(new_pos)

    def _home(self):
        self.model.instrument.home()
        self.model.instrument.set_settings(position=Position(2262.92, 2137.09, 0, 0))
        logger.debug("Scanner at home. Scanner position is:")
        current_position = self.model.instrument.position()
        logger.debug(f'x: {current_position.x}')
        logger.debug(f'y: {current_position.y}')
        logger.debug(f'z: {current_position.z}')
        logger.debug(f'w: {current_position.z}')

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
