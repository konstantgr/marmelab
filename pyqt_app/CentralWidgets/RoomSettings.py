from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy
from .QSmartTable import QSmartTable, Setting, Length


class RoomSettings(QWidget):
    def __init__(self):
        super(RoomSettings, self).__init__()
        layout = QVBoxLayout()
        settings = [
            Setting('test', Length, 1, 'kek', float),
            Setting('test2', Length, 1, 'kek1', float)
        ]
        table = QSmartTable(settings)
        layout.addWidget(table)
        self.setLayout(layout)
