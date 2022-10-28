from src.scanner_utils import *
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, QVBoxLayout, QFrame, QLineEdit, QHBoxLayout, QSplitter, QApplication
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt5 import QtGui

from PyQt5 import QtGui
from PyQt6.QtWidgets import QApplication, QWidget, QFrame, QLineEdit, QHBoxLayout, QSplitter, QRadioButton
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
        layout = QHBoxLayout()
        self.setLayout(layout)
        button1 = QPushButton("Abort")
        button2 = QPushButton("Current position is..")
        button3 = QPushButton("Home")

        layout.addWidget(button3)
        layout.addWidget(button1)
        layout.addWidget(button2)

        button1.clicked.connect(f_abort)
        button2.clicked.connect(f_currrent_position)
        button3.clicked.connect(f_home)
