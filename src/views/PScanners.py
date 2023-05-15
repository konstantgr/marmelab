from PyQt6.QtWidgets import QSplitter, QLabel
from PyQt6.QtWidgets import QWidget, QSizePolicy, QLineEdit, QGroupBox, QHBoxLayout, QVBoxLayout, QFormLayout
from .Widgets import SettingsTableWidget, StateDepPushButton
from ..Variable import Setting
from ..project.PScanners import TRIMPScanner
from ..scanner.scanner import Position
from PyQt6.QtCore import Qt, QThreadPool
from .View import BaseView, QWidgetType
from PyQt6.QtCore import QRegularExpression
from PyQt6.QtGui import QRegularExpressionValidator
from .Widgets import FormLikeInput
from .description import description_scanner

import logging
logger = logging.getLogger()


class TRIMControl(BaseView[TRIMPScanner]):
    def __init__(self, *args, **kwargs):
        super(TRIMControl, self).__init__(*args, **kwargs)
        states = self.model.states
        self.coord_input_model = FormLikeInput.Model(keys=['x', 'y', 'z', 'w'])

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

        self.goto_button = StateDepPushButton(
            state=m_state,
            text="Go",
        )
        self.goto_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)

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
        group_control.setLayout(QVBoxLayout())
        group_control.layout().setAlignment(Qt.AlignmentFlag.AlignLeft)
        group_control.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
        vbox.addWidget(group_control)

        coord_input_widget = FormLikeInput.View(
            model=self.coord_input_model
        )
        coord_input_widget.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Maximum)
        group_control.layout().addWidget(coord_input_widget)
        group_control.layout().addWidget(self.goto_button)
        self.goto_button.clicked.connect(self.goto)

        description_text = QLabel()
        description_text.setAlignment(Qt.AlignmentFlag.AlignTop)
        description_text.setText(description_scanner)

        widget.layout().addWidget(description_text)
        return widget

    def goto(self):
        x = self.coord_input_model.get_parsed_value('x')
        y = self.coord_input_model.get_parsed_value('y')
        z = self.coord_input_model.get_parsed_value('z')
        w = self.coord_input_model.get_parsed_value('w')
        self.model.custom_goto(x, y, z, w)

    def _home(self):
        self.model.custom_home()

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
