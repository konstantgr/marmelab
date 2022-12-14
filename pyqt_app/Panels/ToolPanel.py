from PyQt6.QtWidgets import QPushButton, QToolBar, QMainWindow
from PyQt6.QtCore import pyqtSignal, pyqtBoundSignal
from pyqt_app import project
from pyqt_app import logger


class ToolPanel(QToolBar):
    def __init__(self, *args, **kwargs):
        super(QToolBar, self).__init__(*args, **kwargs)
        self.upd_button = QPushButton("Update current position")
        self.addWidget(self.upd_button)

    def f_upd_cur_pos(self):
        logger.debug("Scanner position is:")
        current_position = scanner.position()
        logger.debug('x: ', current_position.x)
        logger.debug('y: ', current_position.y)
        logger.debug('z: ', current_position.z)

