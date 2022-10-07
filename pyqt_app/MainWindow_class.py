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



    def button_maker(self, text, b_text, x_coor, y_coor, above_text, b_size_w, b_size_h):
        self.b_size_w = b_size_w  # размер кнопки по х
        self.b_size_h = b_size_h  # размер кнопки по у
        self.x_coor = x_coor  # координата кнопки по х
        self.y_coor = y_coor  # координата кнопки по у
        self.text = text  # текст над кнопкой
        self.b_text = b_text  # имя кнопки
        self.above_text = above_text  # текст всплывающего окна

        self.button = QPushButton(b_text, self)
        self.button.setCheckable(True)
        self.button.setToolTip(above_text)
        #button.clicked.connect(self.the_button_was_clicked)
        self.button.setFixedWidth(b_size_w)
        self.button.setFixedHeight(b_size_h)
        self.button.move(x_coor, y_coor)

    def the_button_was_clicked(self):

        # self.setCentralWidget(button)
        # start_time = time()
        # random_matmul()[0, 0]
        # print(time() - start_time)
        print("connected")
        self.show()
