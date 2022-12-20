from src.project.Widgets import StateDepPushButton
from PyQt6.QtWidgets import QToolBar
from pyqt_app import project
import logging
logger = logging.getLogger()


class ToolPanel(QToolBar):
    def __init__(self, *args, **kwargs):
        super(QToolBar, self).__init__(*args, **kwargs)
        self.upd_button = StateDepPushButton(
            state=project.scanner.states.is_connected,
            text="Update current position",
            parent=self
        )
        self.addWidget(self.upd_button)
        self.upd_button.clicked.connect(self.f_upd_cur_pos)

    def f_upd_cur_pos(self):
        project.scanner.instrument.position()



