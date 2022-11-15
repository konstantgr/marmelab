from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QHBoxLayout
from .QSmartTable import QSmartTable, Variable, Length, NoUnit, Time, Frequency
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt


class RoomSettings(QWidget):
    def __init__(self):
        super(RoomSettings, self).__init__()
        self.layout = QVBoxLayout()
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.layout)

        settings = [
            Variable(name='test', unit=NoUnit, default_value=1, description='kek', type=float),
            Variable(name='test2', unit=Length, default_value=2, description='kek12394 324 j234k 23j4lk2j 4j2k l4j2j 2lk3 j42lk3j 4lk23j4 k2j4 3', type=float)
        ]
        self.table = QSmartTable(settings)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Maximum)
        self.layout.addWidget(self.table)

        buttons_layout = QHBoxLayout()
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        set_default_button = QtWidgets.QPushButton("Set default")
        set_default_button.clicked.connect(self.table.set_default)
        set_default_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        buttons_layout.addWidget(set_default_button)

        apply_button = QtWidgets.QPushButton("Apply")
        apply_button.clicked.connect(self.apply)
        apply_button.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum)
        buttons_layout.addWidget(apply_button)
        buttons_layout.setStretch(0, 1)
        buttons_layout.setStretch(1, 1)

        self.layout.addLayout(buttons_layout)


    def apply(self):
        print(self.table.to_dict())
