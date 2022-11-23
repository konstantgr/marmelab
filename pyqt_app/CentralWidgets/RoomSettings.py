from PyQt6.QtWidgets import QWidget, QVBoxLayout, QSizePolicy, QHBoxLayout, QSplitter, QHeaderView
from .QSmartTable import QSmartTable, Variable, Length, NoUnit, Time, Frequency
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6.QtCore import pyqtBoundSignal, pyqtSignal, QObject


class RoomSettings(QWidget):
    settings_signal: pyqtBoundSignal = pyqtSignal(dict)

    def __init__(self, default_settings: dict):
        super(RoomSettings, self).__init__()
        self.splitter = QSplitter(orientation=Qt.Orientation.Vertical)
        self.layout = QVBoxLayout()
        self.layout.addWidget(self.splitter)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.layout)
        self.default_settings = default_settings

        settings = []
        for key, value in self.default_settings.items():
            for i, suffix in enumerate(['x', 'y', 'z']):
                setting = Variable(name=key + suffix, unit=Length, default_value=value[i], description="", type=float)
                settings.append(setting)

        self.table = QSmartTable(settings)
        self.table.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setFixedHeight(340)
        self.splitter.addWidget(self.table)

        buttons_widget = QWidget()
        buttons_layout = QHBoxLayout()
        buttons_widget.setLayout(buttons_layout)
        buttons_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        # buttons_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

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

        self.splitter.addWidget(buttons_widget)

    def apply(self):
        user_settings = self.table.to_dict()
        settings = {}
        for key, value in self.default_settings.items():
            r = []
            for i, suffix in enumerate(['x', 'y', 'z']):
                r.append(user_settings.get(key + suffix))
            settings[key] = tuple(r)
        self.settings_signal.emit(settings)
