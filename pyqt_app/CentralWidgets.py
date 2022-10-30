from src.scanner_utils import *
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, QVBoxLayout, QFrame, QLineEdit, QHBoxLayout, QSplitter, QApplication, QSpinBox
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt5 import QtGui

from PyQt5 import QtGui
from PyQt6.QtWidgets import QApplication, QWidget, QFrame, QLineEdit, QHBoxLayout, QSplitter, QRadioButton, QPlainTextEdit
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

        text_window1 = QPlainTextEdit(self)
        text_window1.setFixedWidth(30)
        text_window1.setFixedHeight(30)
        arrow_window1 = QSpinBox(self)  #ввод координаты

        layout.addWidget(button3)
        layout.addWidget(button1)
        layout.addWidget(button2)
        layout.addWidget(text_window1)
        layout.addWidget(arrow_window1)
        layout.addWidget(button4)


        button1.clicked.connect(f_abort)
        button2.clicked.connect(f_currrent_position)
        button3.clicked.connect(f_home)
        #button4.clicked.connect(f_X_positive(arrow_window1.value())) # надо в функцию передать значения, которое введется в QSpinBox
        button4.clicked.connect(f_X_positive(12)) # надо в функцию передать значения, которое введется в QSpinBox НЕ работает
