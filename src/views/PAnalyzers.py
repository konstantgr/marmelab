from PyQt6.QtWidgets import QSplitter
from PyQt6.QtWidgets import QWidget, QSizePolicy, QGroupBox, QVBoxLayout
from .Widgets import SettingsTableWidget, StateDepPushButton
from ..Variable import Setting
from ..scanner.scanner import Position
from PyQt6.QtCore import Qt, QThreadPool
from .View import BaseView, QWidgetType
from ..project.Project import PAnalyzer

import logging
logger = logging.getLogger()


class SocketAnalyzerControl(BaseView[PAnalyzer]):
    def __init__(self, *args, **kwargs):
        super(SocketAnalyzerControl, self).__init__(*args, **kwargs)
        states = self.model.states

        self.connect_button = StateDepPushButton(
            state=~states.is_connected & ~states.is_in_use,
            text="Connect",
        )

        m_state = states.is_connected & ~states.is_in_use
        self.disconnect_button = StateDepPushButton(
            state=m_state,
            text="Disconnect",
        )

    def construct_widget(self) -> QWidgetType:
        widget = QWidget()
        vbox = QVBoxLayout(widget)
        vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        widget.setLayout(vbox)

        group = QGroupBox(widget)
        group_layout = QVBoxLayout(group)
        group_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        vbox.addWidget(group)

        self.connect_button.clicked.connect(self.model.instrument.connect)
        self.disconnect_button.clicked.connect(self.model.instrument.disconnect)

        group_layout.addWidget(self.connect_button)
        group_layout.addWidget(self.disconnect_button)

        return widget

    def display_name(self) -> str:
        return self.model.name
