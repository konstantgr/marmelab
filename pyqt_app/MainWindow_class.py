import CentralWidgets
import LogWidget
import logging
import sys
from PyQt6 import QtWidgets
from PyQt6.QtWidgets import (QApplication, QWidget, QFrame, QLineEdit, QHBoxLayout, QSplitter, QMainWindow, QPushButton,
                             QGridLayout, QVBoxLayout, QSplitter, QStackedWidget, QListWidget,
                             QFormLayout, QRadioButton, QLabel, QCheckBox, QDialog, QPlainTextEdit, QMenuBar, QTextEdit)
import sys
from PyQt6.QtCore import Qt, pyqtSignal as Signal, QObject
from enum import IntEnum, auto

# TODO: Зафиксировать левый виджет?
# TODO: оптимизация процесса создания кнопок

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
        super(CentralPanel, self).__init__(*args, **kwargs)

        pages = {
            CentralPanelTypes.Initial: CentralWidgets.Init(),
            CentralPanelTypes.ScannerSettings: CentralWidgets.ScannerSettings(),
            CentralPanelTypes.Scanner: CentralWidgets.ScannerControl(),
            CentralPanelTypes.Next: CentralWidgets.ScannerControl(),

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
        self.menu_bar = QMenuBar()

        self.text_edit = QTextEdit()

        self.OUTPUT_LOGGER_STDOUT = LogWidget.OutputLogger(sys.stdout, LogWidget.OutputLogger.Severity.DEBUG)
        self.OUTPUT_LOGGER_STDERR = LogWidget.OutputLogger(sys.stderr, LogWidget.OutputLogger.Severity.ERROR)

        sys.stdout = self.OUTPUT_LOGGER_STDOUT
        sys.stderr = self.OUTPUT_LOGGER_STDERR

        self.OUTPUT_LOGGER_STDOUT.emit_write.connect(self.append_log)
        self.OUTPUT_LOGGER_STDERR.emit_write.connect(self.append_log)

        menu = self.menu_bar.addMenu('Say')  # Как настроить вывод....
        menu.addAction('hello', lambda: print('Hello!'))
        menu.addAction('fail', lambda: print('Fail!', file=sys.stderr))
        hbox.addWidget(self.menu_bar)
        self.setLayout(hbox)

    def append_log(self, text, severity):
        text = repr(text)

        if severity == LogWidget.OutputLogger.Severity.ERROR:
            text = '<b>{}</b>'.format(text)

        self.text_edit.append(text)


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
