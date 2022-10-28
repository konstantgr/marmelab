import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, QVBoxLayout, QFrame, QLineEdit, QHBoxLayout, QSplitter, QApplication
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt5 import QtGui

from PyQt5 import QtGui
from PyQt6.QtWidgets import QApplication, QWidget, QFrame, QLineEdit, QHBoxLayout, QSplitter, QRadioButton
import sys
from PyQt6.QtCore import Qt


class Init(QWidget):
    """

    """
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.addWidget(QPushButton("test2"))
        layout.addWidget(QPushButton("tes123t2"))
        layout.addWidget(QPushButton("te2112t2"))
        # если я хочу иметь и виджет и строку и черта лысого я должне для каждого создать свой слой?


class Scanner(QWidget):
    """

    """

    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.addWidget(QPushButton("test1"))
        layout.addWidget(QRadioButton("Male"))
        layout.addWidget(QRadioButton("Female"))
