from PyQt6.QtWidgets import QStatusBar
from .BasePanel import BasePanel
from PyQt6.QtCore import pyqtSignal, pyqtBoundSignal, QObject

class BarPanel(BasePanel):
    def __init__(self, *args, **kwargs):
        super(BarPanel, self).__init__(*args, **kwargs)
        self.bar = QStatusBar()


