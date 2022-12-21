from src.project.Widgets import StateDepPushButton
from PyQt6.QtWidgets import QToolBar, QPushButton
from pyqt_app import project
import logging
from pyqt_app.app_project import path_adder
logger = logging.getLogger()


class ToolPanel(QToolBar):
    def __init__(self, *args, **kwargs):
        super(QToolBar, self).__init__(*args, **kwargs)
        self.upd_button = QPushButton("Update current position")
        self.add_path_button = QPushButton("Add path")
        self.add_obj_button = QPushButton("Add object")
        self.abort_button = StateDepPushButton(
            state=project.scanner.states.is_connected,
            text="Abort",
            parent=self
        )
        self.abort_button.setProperty('color', 'red')

        self.addWidget(self.upd_button)
        self.addWidget(self.add_path_button)
        self.addWidget(self.add_obj_button)
        self.addWidget(self.abort_button)

        self.add_path_button.clicked.connect(path_adder)
        self.upd_button.clicked.connect(self.f_upd_cur_pos)

    def f_upd_cur_pos(self):
        project.scanner.instrument.position()



