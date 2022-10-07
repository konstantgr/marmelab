import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton
from PyQt6 import QtWidgets
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from src.matmul import random_matmul
from time import time
from TRIM import TRIMScanner
from tests.TRIM_emulator import run

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
        # main_text = QtWidgets.QLabel(self)
        # main_text.setText(self.text)
        # main_text.move(self.x_coor, self.y_coor - 30)


    def button_maker(self, text, b_text, x_coor, y_coor, above_text, b_size_w, b_size_h, func):
        button = QPushButton(b_text, self)

        button.setCheckable(True)
        button.setToolTip(above_text)
        button.clicked.connect(func)
        button.setFixedWidth(b_size_w)
        button.setFixedHeight(b_size_h)
        button.move(x_coor, y_coor)
        #self.setCentralWidget(button)
        #self.show()


