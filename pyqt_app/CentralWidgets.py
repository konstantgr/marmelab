from TableWidgets import *
from src.scanner_utils import *
import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, QVBoxLayout,
                             QFrame, QLineEdit, QHBoxLayout, QSplitter, QApplication, QSpinBox, QPlainTextEdit, QTableWidget, QHeaderView, QTableWidgetItem)

from PyQt6.QtCore import Qt


class SettingsTable(QTableWidget):
    """
    таблица настроек сканера.

    """
    def __init__(self):
        pass





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

        self.button_apply = QPushButton("Apply")
        self.button_default_set = QPushButton("Default settings")  # должны подтягивать настройки с трим сканнера

        self.button_apply.clicked.connect(self.apply_settings)
        self.button_default_set.clicked.connect(self.apply_settings)  #  заглушка


        # формирование таблицы
        self.table_widget = QTableWidget(6, 4)
        self.table_widget.setColumnWidth(0, 50)
        self.table_widget.setColumnWidth(1, 50)
        self.table_widget.setColumnWidth(2, 50)
        self.table_widget.setColumnWidth(3, 50)
        self.table_widget.setVerticalHeaderLabels(("Acceleration", "Deceleration", "Velocity", "Motion mode", "Special motion mode", "Motor on / off"))
        self.table_widget.setHorizontalHeaderLabels(("X", "Y", "Z", "W"))
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_widget.setFixedSize(300, 206)
        self.table_widget.setSpan(3, 0, 1, 4)  # слияние столбцов
        self.table_widget.setSpan(4, 0, 1, 4)
        self.table_widget.setSpan(5, 0, 1, 4)

        chkBoxItem = QTableWidgetItem()
        chkBoxItem.setFlags(Qt.ItemFlag.ItemIsUserCheckable | Qt.ItemFlag.ItemIsEnabled)
        chkBoxItem.setCheckState(Qt.CheckState.Unchecked)
        self.table_widget.setItem(5, 0, chkBoxItem)


        # добавление всех виджетов в слои
        self.layout().addWidget(self.table_widget)
        self.layout().addWidget(self.button_apply)
        self.layout().addWidget(self.button_default_set)




    def apply_settings(self):
        print(int(self.table_widget.item(1, 1).text()))



class Scanner(QWidget):
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

        # формирование таблицы, в которой задаются значения координат, скоростей и шага для трех осей
        tableWidget = QTableWidget(4, 3)
        tableWidget.setColumnWidth(0, 50)
        tableWidget.setColumnWidth(1, 50)
        tableWidget.setColumnWidth(2, 50)
        tableWidget.setColumnWidth(3, 50)
        tableWidget.setHorizontalHeaderLabels(("Coord.", "Speed", "Step"))
        tableWidget.setVerticalHeaderLabels(("X", "Y", "Z", "W"))
        tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tableWidget.setFixedSize(150, 150)

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