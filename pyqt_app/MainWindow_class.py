import CentralWidgets
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import (QApplication, QWidget, QFrame, QLineEdit, QHBoxLayout, QSplitter, QMainWindow, QPushButton,
                             QGridLayout, QWidget, QVBoxLayout, QSplitter, QApplication,
                             QStackedWidget, QListWidget, QFormLayout, QRadioButton, QLabel, QCheckBox)
import sys
from tkinter import messagebox
from PyQt6.QtCore import Qt
from enum import IntEnum, auto
# TODO: Зафиксировать левый виджет?
# TODO: оптимизация процесса создания кнопок
# TODO: изъян: легко запутаться в соответствии кнопок справа и слева. Важен порядок, и надо зависимость от порядка убрать
# TODO: разобраться как с помощью таблицы управлять сканером
# TODO:

class CentralPanelTypes(IntEnum):
    """
    замена цифр на названия
    """
    Initial: int = auto()
    ScannerSettings: int = auto()
    Scanner: int = auto()
    Next: int = auto()

class BasePanel(QFrame):
    """
    This class makes base construction for all panel
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.setFrameShape(QFrame.Shape.StyledPanel)


class LeftPanel(BasePanel):
    """
    This class makes widgets on the left panel
    """
    def __init__(self, *args, **kwargs):
        """
        Формирование стеков виджетов на левой панели
        """
        super().__init__(*args, **kwargs)
        self.leftlist = QListWidget()
        self.leftlist.insertItem(CentralPanelTypes.Initial, 'Initial')
        self.leftlist.insertItem(CentralPanelTypes.ScannerSettings, 'Scanner settings')
        self.leftlist.insertItem(CentralPanelTypes.Scanner, 'Scanner')
        self.leftlist.insertItem(CentralPanelTypes.Next, 'Next')
        # обращение к виджетам из центр. указывает на номер отображаемого виджета

        hbox = QHBoxLayout(self)
        hbox.addWidget(self.leftlist)
        self.setLayout(hbox)


class RightPanel(BasePanel):
    """
    This class makes widgets on the right panel
    """


class CentralPanel(QStackedWidget, BasePanel):
    """
    This class makes widgets on the central panel
    """
    def __init__(self, *args, **kwargs):
        """
        создание виджетов в центр. панели. В слои они добовляются в классе централ виджет
        """
        super(CentralPanel, self).__init__(*args, **kwargs)  # инициализация экзмепляров родительского класса. ТО есть есть все свой-ва бэйз панел

        pages = {
            CentralPanelTypes.Initial: CentralWidgets.Init(),
            CentralPanelTypes.ScannerSettings: CentralWidgets.ScannerSettings(),
            CentralPanelTypes.Scanner: CentralWidgets.Scanner(),
            CentralPanelTypes.Next: CentralWidgets.Scanner(),

        }

        for key in pages.keys():
            self.insertWidget(key, pages[key]) #  добавленеи виджетов в центральную панель


    def display(self, i):
        self.setCurrentIndex(i)


class LogPanel(BasePanel):
    """
    This class makes widgets on the log panel
    """


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main_widget = QWidget()
        hbox = QHBoxLayout(self.main_widget)  # layout of Main window
        self.main_widget.setLayout(hbox)

        self.left_panel = LeftPanel(self.main_widget)  # settings selector
        self.center_panel = CentralPanel(self.main_widget)  # settings menu
        self.right_panel = RightPanel(self.main_widget)  # graphics
        self.log_panel = LogPanel(self.main_widget)  # log window
        self.left_panel.leftlist.currentRowChanged.connect(self.center_panel.display) # связь левой панели и центр виджета

        splitter2 = QSplitter(orientation=Qt.Orientation.Horizontal)
        splitter2.addWidget(self.left_panel)
        splitter2.setSizes([35])#  фиксированая ширина левого окна
        splitter2.addWidget(self.center_panel)
        splitter2.setGeometry(100, 100, 100, 100)
        splitter2.setStretchFactor(0, 0)  # попытка зафиксировать левое окно

        splitter1 = QSplitter(orientation=Qt.Orientation.Vertical)
        splitter1.insertWidget(0, splitter2)
        splitter1.insertWidget(1, self.log_panel)


        splitter0 = QSplitter(orientation=Qt.Orientation.Horizontal)
        splitter0.insertWidget(0, splitter1)
        splitter0.insertWidget(1, self.right_panel)
        splitter0.setSizes([50, 450])  # фиксированая ширина левого окна

        hbox.addWidget(splitter0)

        self.setGeometry(300, 300, 450, 400)
        self.setWindowTitle('Scanner control')
        self.setCentralWidget(self.main_widget)

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

