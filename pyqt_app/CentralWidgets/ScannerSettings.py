from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QSizePolicy, QTableWidget, QHeaderView, QTableWidgetItem

from TRIM import DEFAULT_SETTINGS
from pyqt_app import scanner
from src import BaseAxes


class ScannerSettings(QWidget):
    """

    """
    def __init__(self):
        super(ScannerSettings, self).__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.button_apply = QPushButton("Apply")
        self.button_apply.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum))
        self.button_default_set = QPushButton("Default settings")  # должны подтягивать настройки с трим сканнера
        self.button_default_set.setSizePolicy(QSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Maximum))

        self.button_apply.clicked.connect(self.apply_settings)
        self.button_default_set.clicked.connect(self.set_default_settings)

        # формирование таблицы

        self.settings_keys = {
            'acceleration': "Acceleration",
            'deceleration': "Deceleration",
            'velocity': "Velocity",
            'motion_mode': "Motion mode",
            'special_motion_mode': "Special motion mode",
            'motor_on': "Motor on / off"
        }

        self.table_widget = QTableWidget(len(self.settings_keys), 4)
        self.table_widget.setColumnWidth(0, 50)
        self.table_widget.setColumnWidth(1, 50)
        self.table_widget.setColumnWidth(2, 50)
        self.table_widget.setColumnWidth(3, 50)
        self.table_widget.setVerticalHeaderLabels(self.settings_keys.values())
        self.table_widget.setHorizontalHeaderLabels(("X", "Y", "Z", "W"))
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_widget.setFixedHeight(300)

        self.layout().addWidget(self.table_widget)
        self.layout().addWidget(self.button_apply)
        self.layout().addWidget(self.button_default_set)

    def settings_to_dict(self):
        user_settings = {}
        for key, value in DEFAULT_SETTINGS.items():
            #logger.info(f"{key}")
            j = list(self.settings_keys.keys()).index(key)
            cl = value.__class__ if isinstance(value.__class__, BaseAxes) else BaseAxes
            x = self.table_widget.item(j, 0)
            y = self.table_widget.item(j, 1)
            z = self.table_widget.item(j, 2)
            w = self.table_widget.item(j, 3)

            user_settings[key] = cl(
                x=x if x is None else float(x.text()),
                y=y if y is None else float(y.text()),
                z=z if z is None else float(z.text()),
                w=w if w is None else float(w.text()),
            )
        return user_settings

    def set_default_settings(self):
        for j, key in enumerate(self.settings_keys):
            setting = DEFAULT_SETTINGS.get(key)

            if isinstance(setting, BaseAxes):
                x, y, z, w = setting.x, setting.y, setting.z, setting.w
            else:
                x = y = z = w = setting.A
            self.table_widget.setItem(j, 0, QTableWidgetItem(str(x)))
            self.table_widget.setItem(j, 1, QTableWidgetItem(str(y)))
            self.table_widget.setItem(j, 2, QTableWidgetItem(str(z)))
            self.table_widget.setItem(j, 3, QTableWidgetItem(str(w)))

    def apply_settings(self):
        scanner.set_settings(**self.settings_to_dict())


