from src.views.Widgets import StateDepPushButton, StateDepQAction
from PyQt6.QtWidgets import QToolBar, QPushButton
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import QSize
from pyqt_app import project, builder
from src.Builder import FactoryGroups
import logging
from src.icons import arrow_circle_24
from src.icons import cross
from functools import partial
import numpy as np
logger = logging.getLogger()


class ToolPanel(QToolBar):
    def __init__(self, *args, **kwargs):
        super(QToolBar, self).__init__(*args, **kwargs)
        self.setIconSize(QSize(24, 24))
        self.abort_button = StateDepQAction(
            state=project.scanner.states.is_connected,
            set_icon=cross,
            text="Abort",
            parent=self
        )

        self.upd_button_action = StateDepQAction(
            state=project.scanner.states.is_connected,
            set_icon=arrow_circle_24,
            text="Update current position",
            parent=self
        )

        self.upd_button_action.triggered.connect(project.scanner.instrument.position)
        self.abort_button.triggered.connect(project.scanner.instrument.abort)

        self.addAction(self.upd_button_action)
        self.addAction(self.abort_button)

        for group, factories in builder.factories.items():
            if group in (FactoryGroups.scanners, FactoryGroups.analyzers):
                continue
            for factory in factories:
                button = QPushButton(f'Add {factory.type.type_name}')
                self.addWidget(button)
                button.clicked.connect(
                    partial(factory.create, project=project)
                )
