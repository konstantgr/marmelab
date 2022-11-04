import logging

from src.scanner import BaseAxes
from TRIM import TRIMScanner, DEFAULT_SETTINGS
from src.scanner_utils import *
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, QVBoxLayout,
                             QFrame, QLineEdit, QHBoxLayout, QSplitter, QApplication, QSpinBox, QPlainTextEdit, QTableWidget, QHeaderView, QTableWidgetItem)

from PyQt6.QtCore import Qt

logger = logging.getLogger()

class Init(QWidget):
    """

    """
    def __init__(self):
        super().__init__()
        """
        This function makes connection to the scanner
        """
        layout = QHBoxLayout()
        self.setLayout(layout)
        button = QPushButton("Connect")
        layout.addWidget(button)
        button.clicked.connect(f_connection)


class ScannerSettings(QWidget):
    """

    """
    def __init__(self):
        super(ScannerSettings, self).__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.button_apply = QPushButton("Apply")
        self.button_default_set = QPushButton("Default settings")  # должны подтягивать настройки с трим сканнера

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
        # self.table_widget.setSpan(3, 0, 1, 4)  # слияние столбцов
        # self.table_widget.setSpan(4, 0, 1, 4)
        # self.table_widget.setSpan(5, 0, 1, 4)

        # chkBoxItem = QTableWidgetItem()
        # chkBoxItem.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        # chkBoxItem.setCheckState(Qt.CheckState.Unchecked)
        # self.table_widget.setItem(5, 0, chkBoxItem)

        # добавление всех виджетов в слои
        self.layout().addWidget(self.table_widget)
        self.layout().addWidget(self.button_apply)
        self.layout().addWidget(self.button_default_set)

    def settings_to_dict(self):
        user_settings = {}
        for key, value in DEFAULT_SETTINGS.items():
            j = list(self.settings_keys.keys()).index(key)
            cl = value.__class__ if isinstance(value.__class__, BaseAxes) else BaseAxes
            x = self.table_widget.item(j, 0)
            y = self.table_widget.item(j, 1)
            z = self.table_widget.item(j, 2)
            w = self.table_widget.item(j, 3)

            user_settings[key] = cl(
                x=x if x is None else int(x.text()),
                y=y if y is None else int(y.text()),
                z=z if z is None else int(z.text()),
                w=w if w is None else int(w.text()),
            )
        return user_settings

    def set_default_settings(self):
        for j, key in enumerate(self.settings_keys):
            setting = DEFAULT_SETTINGS.get(key)
            logger.info(f"{j} {key}")

            if isinstance(setting, BaseAxes):
                x, y, z, w = setting.x, setting.y, setting.z, setting.w
            else:
                x = y = z = w = setting.A
            self.table_widget.setItem(j, 0, QTableWidgetItem(str(x)))
            self.table_widget.setItem(j, 1, QTableWidgetItem(str(y)))
            self.table_widget.setItem(j, 2, QTableWidgetItem(str(z)))
            self.table_widget.setItem(j, 3, QTableWidgetItem(str(w)))

    def apply_settings(self):
        sc.set_settings(**self.settings_to_dict())


class ScannerControl(QWidget):
    """

    """

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        button_abort = QPushButton("Abort")
        button_current_pos = QPushButton("Current position is..")
        button_home = QPushButton("Home")
        button_x = QPushButton("x")
        button_go = QPushButton("Go")

        arrow_window1 = QSpinBox(self)  #ввод координаты

        #  создание горизонтального слоя внутри вертикального для окна с выбором значения координаты и кнопки перемещения по оси х по заданной координате
        layout1 = QHBoxLayout()
        widget1 = QWidget()
        widget1.setLayout(layout1)
        layout1.addWidget(arrow_window1)
        layout1.addWidget(button_x)

        #  создание горизонтального слоя внутри вертикального для помещения туда таблицы и кнопок пуск и аборт
        layout2 = QHBoxLayout()
        widget2 = QWidget()
        widget2.setLayout(layout2)
        layout2.setAlignment(Qt.AlignmentFlag.AlignTop)
        # формирование таблицы, в которой задаются значения координат, скоростей и шага для трех осей
        tableWidget = QTableWidget(4, 3)
        # tableWidget.setColumnWidth(0, 50)
        # tableWidget.setColumnWidth(1, 50)
        # tableWidget.setColumnWidth(2, 50)
        # tableWidget.setColumnWidth(3, 50)
        tableWidget.setHorizontalHeaderLabels(("Coord.", "Speed", "Step"))
        tableWidget.setVerticalHeaderLabels(("X", "Y", "Z", "W"))
        tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        #tableWidget.setFixedSize(150, 150)

        layout2.addWidget(tableWidget)
        layout2.addWidget(button_go)
        layout2.addWidget(button_abort)

        # добавление всех виджетов в основной слой
        layout.addWidget(button_home)
        layout.addWidget(button_current_pos)
        layout.addWidget(widget1)  # добавление горизонтального виджета в вертикальный слой
        layout.addWidget(widget2)  # добавление горизонтального виджета в вертикальный слой

        # определение функционала кнопок
        button_abort.clicked.connect(f_abort)  #заглушка
        button_current_pos.clicked.connect(f_currrent_position)
        button_home.clicked.connect(f_home)
        button_x.clicked.connect(lambda x: f_X_positive(arrow_window1.value()))

        button_go.clicked.connect(lambda x: f_go_table(int(tableWidget.item(1, 1).text()), 10, 10))