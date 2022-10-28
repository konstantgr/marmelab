import CentralWidgets
from PyQt6.QtWidgets import QMainWindow, QPushButton, QGridLayout, QWidget, QVBoxLayout, QSplitter, QApplication
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication, QWidget, QFrame, QLineEdit, QHBoxLayout, QSplitter, QStackedWidget, QListWidget, QFormLayout, QRadioButton, QLabel, QCheckBox
import sys
from PyQt6.QtCore import Qt

# TODO: Зафиксировать левый виджет
# TODO: описать сплиттеры, функции, классы
# TODO: ветвление
# TODO: оптимизация процесса создания кнопок
# TODO: создать класс кнопок с ветвлением



class BasePanel(QFrame):
    """
    This class makes base construction for all panel
    """
    def __init__(self, parent):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.parent_ = parent  # type: MainWindow
        self.panel_init()



    def panel_init(self):
        """

        :return:
        """
        pass


class LeftPanel(BasePanel):
    """
    This class makes widgets on the left panel
    """
    def panel_init(self):
        """
        Формирование стеков виджетов на левой панели
        """
        self.Stack = QStackedWidget(self)
        self.stack1 = QWidget()
        self.stack2 = QWidget()
        self.stack3 = QWidget()

        self.Stack.addWidget(self.stack1)  # сделать в отдельный класс?
        self.Stack.addWidget(self.stack2)  # сделать в отдельный класс?
        self.Stack.addWidget(self.stack3)  # сделать в отдельный класс?

        self.leftlist = QListWidget()
        self.leftlist.insertItem(0, 'Initial')
        self.leftlist.insertItem(1, 'Scanner')
        self.leftlist.insertItem(2, 'Educational')
        self.leftlist.currentRowChanged.connect(lambda x: self.parent_.center_panel.display)  # обращение к виджетам из центр. указывает на номер отображаемого виджета

        hbox = QHBoxLayout(self)
        hbox.addWidget(self.leftlist)
        hbox.addWidget(self.Stack)
        self.setLayout(hbox)
class RightPanel(BasePanel):
    """
    This class makes widgets on the right panel
    """



class CentralPanel(BasePanel):
    """
    This class makes widgets on the central panel
    """
    def panel_init(self):
        layout = QHBoxLayout()
        self.setLayout(layout)


    def stack1UI(self):
        layout = QFormLayout()
        layout.addRow("Name", QLineEdit())
        layout.addRow("Address", QLineEdit())
        # self.setTabText(0,"Contact Details")
        self.stack1.setLayout(layout)

    def stack2UI(self):
        layout = QFormLayout()
        sex = QHBoxLayout()
        sex.addWidget(QRadioButton("Male"))
        sex.addWidget(QRadioButton("Female"))
        layout.addRow(QLabel("Sex"), sex)
        layout.addRow("Date of Birth", QLineEdit())

        self.stack2.setLayout(layout)

    def stack3UI(self):
        layout = QHBoxLayout()
        layout.addWidget(QLabel("subjects"))
        layout.addWidget(QCheckBox("Physics"))
        layout.addWidget(QCheckBox("Maths"))
        self.stack3.setLayout(layout)

    def display(self, i):
        self.Stack.setCurrentIndex(i)


class LogPanel(BasePanel):
    """
    This class makes widgets on the log panel
    """


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        hbox = QHBoxLayout(self)  # layout of Main window
        self.setLayout(hbox)

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

