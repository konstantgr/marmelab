import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, QVBoxLayout, QFrame, QLineEdit, QHBoxLayout, QSplitter, QApplication
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5 import QtGui

from PyQt5 import QtGui
from PyQt5.QtWidgets import QApplication, QWidget, QFrame, QLineEdit, QHBoxLayout, QSplitter
import sys
from PyQt5.QtCore import Qt


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
# TODO: Реализовать классы для каждого виджета. сделать скелет

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        """
        деление экрана на три части
        """

        hbox = QHBoxLayout(self)

        topleft = QFrame(self)
        topleft.setFrameShape(QFrame.Shape.StyledPanel)

        topright = QFrame(self)
        topright.setFrameShape(QFrame.Shape.StyledPanel)

        bottom = QFrame(self)
        bottom.setFrameShape(QFrame.Shape.StyledPanel)

        splitter1 = QSplitter(Qt.Vertical)
        splitter1.addWidget(topleft)
        hbox.addWidget(splitter1)

        splitter2 = QSplitter(Qt.Vertical)
        splitter2.addWidget(topright)
        hbox.addWidget(splitter2)

        splitter3 = QSplitter(Qt.Vertical)
        splitter3.addWidget(bottom)
        hbox.addWidget(splitter3)



        self.setLayout(hbox)

        self.setGeometry(300, 300, 450, 400)
        self.setWindowTitle('Scanner control')
        self.show()


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
        This function makes a text on the window
        """
        main_text = QtWidgets.QLabel(self)
        main_text.setText(text)
        main_text.move(x, y)

