from src.views.Widgets import StateDepPushButton, StateDepQAction
from PyQt6.QtWidgets import QWidget, QToolBar, QPushButton, QTextEdit, QGroupBox, QHBoxLayout, QVBoxLayout
from PyQt6.QtGui import QAction, QIcon
from PyQt6.QtCore import QSize, Qt
from pyqt_app import project, builder
from src.builder import FactoryGroups
import logging
from src import icons
from functools import partial
import numpy as np
logger = logging.getLogger()


class GroupToolBar(QToolBar):
    def __init__(self, *args, **kwargs):
        super(GroupToolBar, self).__init__(*args, **kwargs)
        self.setIconSize(QSize(32, 32))
        self.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextUnderIcon)


class ToolGroup(QGroupBox):
    def __init__(self, *args, **kwargs):
        super(ToolGroup, self).__init__(*args, **kwargs)
        self.setProperty('type', 'toolbar')
        self.setLayout(QHBoxLayout())
        self.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout().setContentsMargins(0, 0, 0, 0)

    def addQAction(self, action: QAction):
        # ради выравнивания)))))
        group_toolbar = GroupToolBar(parent=self)
        group_toolbar.addAction(action)
        w = QWidget()
        w.setLayout(QVBoxLayout())
        w.layout().setContentsMargins(0, 0, 0, 0)
        w.layout().addWidget(group_toolbar)
        w.layout().setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout().addWidget(w)


class ToolPanel(QToolBar):
    def __init__(self, *args, **kwargs):
        super(QToolBar, self).__init__(*args, **kwargs)
        self.setIconSize(QSize(32, 32))
        self.setMovable(False)

        scanner_group_widget = ToolGroup("Scanner")
        self.addWidget(scanner_group_widget)

        self.abort_button = StateDepQAction(
            state=project.scanner.states.is_connected,
            set_icon=icons.abort,
            text="Abort",
            parent=self
        )
        self.upd_button_action = StateDepQAction(
            state=project.scanner.states.is_connected,
            set_icon=icons.update,
            text="Update\nposition",
            parent=self
        )
        self.upd_button_action.triggered.connect(project.scanner.instrument.position)
        self.abort_button.triggered.connect(self._abort)
        scanner_group_widget.addQAction(self.upd_button_action)
        scanner_group_widget.addQAction(self.abort_button)

        self.addSeparator()
        for group, factories in builder.factories.items():
            group_widget = ToolGroup(group.value)
            group_toolbar = GroupToolBar()
            group_widget.layout().addWidget(group_toolbar)

            i = 0
            for factory in factories:
                if factory.reproducible:
                    i += 1
                    button = QAction(factory.icon, factory.type.type_name, group_toolbar)
                    group_toolbar.addAction(button)
                    button.triggered.connect(
                        partial(factory.create, project=project)
                    )

            if i > 0:
                self.addWidget(group_widget)
                self.addSeparator()

    def _abort(self):
        project.scanner.instrument.abort()
        for experiment in project.experiments.data:
            if experiment.is_running:
                experiment.is_aborted = True
                break

