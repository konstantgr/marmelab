import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, QVBoxLayout
from PyQt6 import QtWidgets
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from src.matmul import random_matmul
from time import time
from TRIM import TRIMScanner
from tests.TRIM_emulator import run
from src import Position
"""
drafts
from src import Position
run(blocking=False)
sc = TRIMScanner(ip="127.0.0.1", port=9000)
sc.connect()
print(sc.velocity().x)
"""


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")
        self.position = Position()
        self.main_widget = QWidget()
        self.main_layout = QGridLayout()
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

        self.left_panel = QWidget()
        self.main_layout.addWidget(self.left_panel, 0, 0)
        self.left_panel.setLayout(QVBoxLayout())
        button1 = QPushButton()
        self.left_panel.layout().addWidget(button1)


        self.right_panel = QWidget()
        self.main_layout.addWidget(self.right_panel, 0, 2)
        self.right_panel.setLayout(QVBoxLayout())
        button2 = QPushButton()
        self.right_panel.layout().addWidget(button2)
        # button = QWidget()
        # layout = QGridLayout()
        # button.setLayout(layout)
        # button = QPushButton()
        # layout.addWidget(button, 0, 1)
        # button = QPushButton()
        # layout.addWidget(button, 1, 0)
        # #layout.addWidget(Color('blue'), 1, 1)
       #layout.addWidget(Color('purple'), 2, 1)



    def button_maker(self, b_text, x_coor, y_coor, above_text, b_size_w, b_size_h, func):
        """
        This function makes push button
        """
        button = QPushButton(b_text, self)
        #button.setCheckable(True)
        button.setToolTip(above_text)
        button.clicked.connect(func)
        button.setFixedWidth(b_size_w)
        button.setFixedHeight(b_size_h)
        button.move(x_coor, y_coor)
        #self.setCentralWidget(button)
        #self.show()

    def field_text_button(self, x_coor, y_coor, b_size_w, b_size_h):
        """
        This function makes button with field, where the text can be added
        """

        field_button = QtWidgets.QPlainTextEdit(self)
        field_button.setFixedWidth(b_size_w)
        field_button.setFixedHeight(b_size_h)
        field_button.move(x_coor, y_coor)
        return field_button

    def text_on_the_window(self, text, x, y):
        """
        """
        main_text = QtWidgets.QLabel(self)
        main_text.setText(text)
        main_text.move(x, y)

