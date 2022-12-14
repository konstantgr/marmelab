from PyQt6.QtWidgets import QPushButton, QToolBar, QMainWindow
from PyQt6.QtCore import pyqtSignal, pyqtBoundSignal
from pyqt_app import project

class ToolPanel(QToolBar):
    def __init__(self, *args, **kwargs):
        super(QToolBar, self).__init__(*args, **kwargs)
        self.upd_button = QPushButton("Update current position")
        self.addWidget(self.upd_button)



