from PyQt6.QtWidgets import QStatusBar
from .BasePanel import BasePanel


class BarPanel(BasePanel):
    def __init__(self, *args, **kwargs):
        super(BarPanel, self).__init__(*args, **kwargs)
        self.bar = QStatusBar()
        self.bar_status = "disconnected"
        self.bar.showMessage("Scanner status: " + self.bar_status)
