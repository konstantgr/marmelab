import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, QVBoxLayout, QFrame, QLineEdit, QHBoxLayout, QSplitter, QApplication
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt5 import QtGui

from PyQt5 import QtGui
from PyQt6.QtWidgets import QApplication, QWidget, QFrame, QLineEdit, QHBoxLayout, QSplitter
import sys
from PyQt6.QtCore import Qt


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
# TODO: Зафиксировать левый виджет
# TODO: описать сплиттеры, функции, классы
# TODO: ветвление



class BasePanel(QFrame):
    """

    description
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.panel_init()

    def panel_init(self):
        """

        :return:
        """
        pass


class LeftPanel(BasePanel):
    """
    ds
    """
    def panel_init(self):
        pass


class RightPanel(BasePanel):
    """
    fdas
    """

class CentralPanel(BasePanel):
    """
    fdas
    """

class LogPanel(BasePanel):
    """
    decr
    """

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        hbox = QHBoxLayout(self)  # layout of Main window

        self.left_panel = LeftPanel(self)  # settings selector
        self.center_panel = CentralPanel(self)  # settings menu
        self.right_panel = RightPanel(self)  # graphics
        self.log_panel = LogPanel(self)  # log window

        splitter2 = QSplitter(orientation=Qt.Orientation.Horizontal)
        splitter2.addWidget(self.left_panel)
        splitter2.setSizes([35])#  фиксированая ширина левого окна
        splitter2.addWidget(self.center_panel)
        splitter2.setGeometry(10, 10, 10, 200)
        splitter2.setStretchFactor(0, 0)  # попытка завфиксировать левое окно

        splitter1 = QSplitter(orientation=Qt.Orientation.Vertical)
        splitter1.insertWidget(0, splitter2)
        splitter1.insertWidget(1, self.log_panel)


        splitter0 = QSplitter(orientation=Qt.Orientation.Horizontal)
        splitter0.insertWidget(0, splitter1)
        splitter0.insertWidget(1, self.right_panel)
        splitter0.setSizes([50, 50])  # фиксированая ширина левого окна

        hbox.addWidget(splitter0)

        self.setLayout(hbox)

        self.setGeometry(300, 300, 450, 400)
        self.setWindowTitle('Scanner control')



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

