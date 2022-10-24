import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, QVBoxLayout, QFrame, QLineEdit, QHBoxLayout, QSplitter, QApplication
from PyQt6 import QtWidgets
from PyQt6.QtCore import Qt
from PyQt6 import QtGui
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

class MainWindow(QMainWindow):
    def __init__(self):
        """
        деление экрана на три части
        """
        super().__init__()
        self.top = 200
        self.left = 500
        self.width = 400
        self.height = 300
        hbox = QHBoxLayout()
        left = QFrame()
        left.setFrameShape(QFrame.StyledPanel)
        bottom = QFrame()
        bottom.setFrameShape(QFrame.StyledPanel)
        splitter1 = QSplitter(Qt.Horizontal)
        splitter1.setStyleSheet('background-color:red')
        lineedit = QLineEdit()
        lineedit.setStyleSheet('background-color:green')
        splitter1.addWidget(left)
        splitter1.addWidget(lineedit)
        splitter1.setSizes([200, 200])
        spliiter2 = QSplitter(Qt.Vertical)
        spliiter2.addWidget(splitter1)
        spliiter2.addWidget(bottom)
        spliiter2.setStyleSheet('background-color:yellow')
        hbox.addWidget(spliiter2)
        self.setLayout(hbox)
        self.setWindowIcon(QtGui.QIcon("icon.png"))
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)
        self.show()

        """
        деление на три виджета кнопкой
        
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
        """



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

