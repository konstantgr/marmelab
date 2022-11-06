import CentralWidgets
import LogWidget
import RightWidgets
import logging
import sys
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import (QApplication, QWidget, QFrame, QLineEdit, QHBoxLayout, QSplitter, QMainWindow, QPushButton,
                             QGridLayout, QVBoxLayout, QSplitter, QStackedWidget, QListWidget,
                             QFormLayout, QRadioButton, QLabel, QCheckBox, QDialog, QPlainTextEdit, QMenuBar, QTextEdit)
import sys
from PyQt6.QtCore import Qt, pyqtSignal as Signal, QObject
from enum import IntEnum, auto

# TODO: сделать нормальное позиционирование всех панелей
# TODO: добавить вкладку с настройками комнаты (таблица/поля, размер комнаты в метрах (x, y ,z),
#  область сканирования (x, y, z) и ее пространственная ориенатция (x, y, z), кнопка apply(pass) )
# TODO: убрать лямбда функции
# TODO: вкладка Next --> Test. реализация кнопки Go, которая измеряет и выдает данные
# TODO: принты (current position) в отдельные окна

logger = logging.getLogger()
logger.setLevel(logging.INFO) # установление уровня выдаваемой информации

class CentralPanelTypes(IntEnum):
    """
    замена цифр на названия
    """
    Initial: int = auto()
    RoomSettings = auto()
    ScannerSettings: int = auto()
    Scanner: int = auto()
    Test: int = auto()


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
        self.leftlist.insertItem(CentralPanelTypes.RoomSettings, 'RoomSettings')
        self.leftlist.insertItem(CentralPanelTypes.ScannerSettings, 'Scanner settings')
        self.leftlist.insertItem(CentralPanelTypes.Scanner, 'Scanner control')
        self.leftlist.insertItem(CentralPanelTypes.Test, 'Test')
        # обращение к виджетам из центр. указывает на номер отображаемого виджета

        hbox = QHBoxLayout(self)
        hbox.addWidget(self.leftlist)
        self.setLayout(hbox)


class RightPanel(BasePanel):
    """
    This class makes widgets on the right panel
    """
    def __init__(self, *args, **kwargs):
        super(RightPanel, self).__init__(*args, **kwargs)

        self.vbox = QVBoxLayout()
        self.setLayout(self.vbox)

        self.scanner_widget = RightWidgets.ScannerVisualizer()
        self.vbox.addWidget(self.scanner_widget)


class CentralPanel(QStackedWidget, BasePanel):
    """
    This class makes widgets on the central panel
    """
    def __init__(self, *args, **kwargs):
        """
        создание виджетов в центр. панели. В слои они добавляются в классе централ виджет
        """
        super(CentralPanel, self).__init__(*args, **kwargs)

        pages = {
            CentralPanelTypes.Initial: CentralWidgets.Init(),
            CentralPanelTypes.RoomSettings: CentralWidgets.RoomSettings(),
            CentralPanelTypes.ScannerSettings: CentralWidgets.ScannerSettings(),
            CentralPanelTypes.Scanner: CentralWidgets.ScannerControl(),
            CentralPanelTypes.Test: CentralWidgets.Test(),

        }

        for key in pages.keys():
            self.insertWidget(key, pages[key])  # добавление виджетов в центральную панель

    def display(self, i):
        self.setCurrentIndex(i)


class LogPanel(BasePanel):
    """
    This class makes widgets on the log panel
    """
    def __init__(self, *args, **kwargs):
        super(LogPanel, self).__init__(*args, **kwargs)
        hbox = QHBoxLayout(self)
        logging_handler = LogWidget.QTextEditLogger(self)
        logging_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s %(levelname)s %(module)s %(funcName)s %(message)s')) # меняет формат сообщения

        hbox.addWidget(logging_handler.widget)
        self.setLayout(hbox)
        logger.addHandler(logging_handler)  # добавление в логгер всего то, что получит обработчик


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
        self.left_panel.leftlist.currentRowChanged.connect(self.center_panel.display)

        splitter2 = QSplitter(orientation=Qt.Orientation.Horizontal)
        splitter2.addWidget(self.left_panel)
        splitter2.addWidget(self.center_panel)

        splitter1 = QSplitter(orientation=Qt.Orientation.Vertical)
        splitter1.insertWidget(0, splitter2)
        splitter1.insertWidget(1, self.log_panel)

        splitter0 = QSplitter(orientation=Qt.Orientation.Horizontal)
        splitter0.insertWidget(0, splitter1)
        splitter0.insertWidget(1, self.right_panel)

        hbox.addWidget(splitter0)

        self.setGeometry(300, 300, 450, 400)
        self.setWindowTitle('Scanner control')
        self.setCentralWidget(self.main_widget)
