import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, QVBoxLayout, QFrame, QLineEdit, QHBoxLayout, QSplitter, QApplication
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt5 import QtGui

from PyQt5 import QtGui
from PyQt6.QtWidgets import QApplication, QWidget, QFrame, QLineEdit, QHBoxLayout, QSplitter
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
        self.setVisible(False)

class Scanner(QWidget):
    """

    """

    def __init__(self):
        super().__init__()
        layout = QHBoxLayout()
        self.setLayout(layout)
        layout.addWidget(QPushButton("test1"))
        self.setVisible(False)
