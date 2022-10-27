import CentralWidgets
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QGridLayout, QWidget, QVBoxLayout, QFrame, QLineEdit, QHBoxLayout, QSplitter, QApplication
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import QApplication, QWidget, QFrame, QLineEdit, QHBoxLayout, QSplitter, QStackedWidget
import sys
from PyQt6.QtCore import Qt, QObject, pyqtSignal, pyqtSlot
from enum import IntEnum, auto

# TODO: Зафиксировать левый виджет
# TODO: описать сплиттеры, функции, классы
# TODO: ветвление
# TODO: оптимизация процесса создания кнопок
# TODO: создать класс кнопок с ветвлением


class CentralPanelsTypes(IntEnum):
    """
    Все возможные типы центральной панели
    """
    INIT = auto()
    SCANNER = auto()


class PanelCommunicator(QObject):
    """
    Класс, который позволяет пересылать сигналы между разными панелями
    """
    set_central_panel = pyqtSignal(int)


class BasePanel(QFrame):
    """
    This class makes base construction for all panel
    """
    def __init__(self, parent: QWidget, communicator: PanelCommunicator):
        super().__init__(parent)
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.communicator = communicator


class LeftPanel(BasePanel):
    """
    This class makes widgets on the left panel
    """
    def __init__(self, *args, **kwargs):
        super(LeftPanel, self).__init__(*args, **kwargs)

        self.vbox = QVBoxLayout()
        self.vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(self.vbox)

        main_init_button = QPushButton("INIT")
        self.vbox.addWidget(main_init_button)
        main_init_button.clicked.connect(self.button_click_0)

        scanner_settings_button = QPushButton("Scanner")
        self.vbox.addWidget(scanner_settings_button)
        scanner_settings_button.clicked.connect(self.button_click_1)

    @pyqtSlot()
    def button_click_0(self):
        self.communicator.set_central_panel.emit(CentralPanelsTypes.INIT)

    @pyqtSlot()
    def button_click_1(self):
        self.communicator.set_central_panel.emit(CentralPanelsTypes.SCANNER)


class RightPanel(BasePanel):
    """
    This class makes widgets on the right panel
    """


class CentralPanel(QStackedWidget, BasePanel):
    """
    This class makes widgets on the central panel
    """
    def __init__(self, *args, **kwargs):
        super(CentralPanel, self).__init__(*args, **kwargs)
        # super(BasePanel, self).__init__()
        # super(QStackedWidget, self).__init__(*args, **kwargs)

        self.all_panels = {
            CentralPanelsTypes.INIT: CentralWidgets.Init(),
            CentralPanelsTypes.SCANNER: CentralWidgets.Scanner()
        }

        for _, panel_widget in self.all_panels.items():
            self.addWidget(panel_widget)
        self.communicator.set_central_panel.connect(self.choose_panel)

    def choose_panel(self, i):
        self.setCurrentWidget(self.all_panels[i])

    # def set_empty(self):
    #     self.a.setVisible(True)
    #     self.b.setVisible(False)
    #     # layout.addWidget(QPushButton("test2"))
    #     # self.update()
    #
    # def set_test(self):
    #     self.a.setVisible(False)
    #     self.b.setVisible(True)


class LogPanel(BasePanel):
    """
    This class makes widgets on the log panel
    """


class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        hbox = QHBoxLayout(self)  # layout of Main window
        self.setLayout(hbox)

        self.panel_communicator = PanelCommunicator()

        self.left_panel = LeftPanel(self, self.panel_communicator)  # settings selector
        self.center_panel = CentralPanel(self, self.panel_communicator)  # settings menu
        self.right_panel = RightPanel(self, self.panel_communicator)  # graphics
        self.log_panel = LogPanel(self, self.panel_communicator)  # log window

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

