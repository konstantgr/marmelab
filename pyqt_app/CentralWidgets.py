from TableWidgets import *
from src.scanner_utils import *
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, QVBoxLayout, QFrame, QLineEdit, QHBoxLayout, QSplitter, QApplication, QSpinBox, QPlainTextEdit, QTableWidget
from PyQt5 import QtGui
from PyQt6.QtCore import Qt


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
        # если я хочу иметь и виджет и строку и черта лысого я должне для каждого создать свой слой?


class Scanner(QWidget):
    """

    """

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        button1 = QPushButton("Abort")
        button2 = QPushButton("Current position is..")
        button3 = QPushButton("Home")
        button4 = QPushButton("x")

        arrow_window1 = QSpinBox(self)  #ввод координаты
        #print(a)
        # формирование таблицы
        tableWidget = QTableWidget(3, 3)
        tableWidget.setColumnWidth(0, 50)
        tableWidget.setColumnWidth(1, 50)
        tableWidget.setColumnWidth(2, 50)
        tableWidget.setColumnWidth(3, 50)
        tableWidget.setHorizontalHeaderLabels(("Coordinate", "Speed", "Step"))
        tableWidget.setVerticalHeaderLabels(("X", "Y", "Z"))

        layout1 = QHBoxLayout()
        widget1 = QWidget()
        widget1.setLayout(layout1)
        #layout1.addWidget(text_window1)
        layout1.addWidget(arrow_window1)
        layout1.addWidget(button4)



        layout.addWidget(button3)
        layout.addWidget(button1)
        layout.addWidget(button2)
        layout.addWidget(widget1)


        layout.addWidget(tableWidget)

        button1.clicked.connect(f_abort)
        button2.clicked.connect(f_currrent_position)
        button3.clicked.connect(f_home)
        #button4.clicked.connect(f_X_positive(arrow_window1.value())) # надо в функцию передать значения, которое введется в QSpinBox
        button4.clicked.connect(lambda x: f_X_positive(arrow_window1.value())) # надо в функцию передать значения, которое введется в QSpinBox НЕ работает
