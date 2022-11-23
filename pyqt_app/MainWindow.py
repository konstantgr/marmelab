import numpy as np
import pandas as pd
import CentralWidgets
import LogWidget
import RightWidgets
from PyQt6.QtWidgets import QWidget, QFrame, QHBoxLayout, QMainWindow, QVBoxLayout, QSplitter, QStackedWidget, QListWidget, QScrollArea, QSizePolicy
from PyQt6.QtCore import Qt
from enum import IntEnum, auto
import logging
from pyqt_app import scanner


# TODO: сделать вывод логов в файл
# TODO: Изменить таблицу сканнер сеттингс
# TODO: Реализация таблицы сканнер контрол (добавить пока что хождение по точкам)
# TODO: ТАблица с настройками объекта и комнаты в рум сеттингс
# TODO: добавить вкладку с настройками комнаты (таблица/поля, размер комнаты в метрах (x, y ,z),
#  область сканирования (x, y, z) и ее пространственная ориенатция (x, y, z), кнопка apply(pass) )
# TODO: убрать лямбда функции
# TODO: вкладка Next --> Test. реализация кнопки Go, которая измеряет и выдает данные
# TODO: ПОСЛЕ ЧЕТВЕРГА
# TODO: добавить в таблицу ск. контролл измерение и запись данных
# TODO: аналогично во вкладке тест

logger = logging.getLogger()


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
        self.leftlist = QListWidget(self)
        self.leftlist.insertItem(CentralPanelTypes.Initial, 'Initial')
        self.leftlist.insertItem(CentralPanelTypes.RoomSettings, 'RoomSettings')
        self.leftlist.insertItem(CentralPanelTypes.ScannerSettings, 'Scanner settings')
        self.leftlist.insertItem(CentralPanelTypes.Scanner, 'Scanner control')
        self.leftlist.insertItem(CentralPanelTypes.Test, 'Test')
        # обращение к виджетам из центр. указывает на номер отображаемого виджета

        hbox = QHBoxLayout(self)
        hbox.addWidget(self.leftlist)
        self.setLayout(hbox)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)


class RightPanel(BasePanel):
    """
    This class makes widgets on the right panel
    """
    def __init__(self, *args, **kwargs):
        super(RightPanel, self).__init__(*args, **kwargs)

        self.vbox = QVBoxLayout(self)
        self.setLayout(self.vbox)

        self.scanner_widget = RightWidgets.ScannerVisualizer(self)
        self.graph_widget = RightWidgets.GraphWidget(self)

        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)

        graphs_splitter = QSplitter(orientation=Qt.Orientation.Vertical)
        graphs_splitter.insertWidget(0, self.scanner_widget)
        graphs_splitter.insertWidget(1, self.graph_widget)
        self.vbox.addWidget(graphs_splitter)

        scanner.position_signal.connect(self.scanner_widget.set_scanner_pos)


class CentralPanel(QScrollArea, BasePanel):
    """
    This class makes widgets on the central panel
    """
    def __init__(self, *args, **kwargs):
        """
        создание виджетов в центр. панели. В слои они добавляются в классе централ виджет
        """
        super(CentralPanel, self).__init__(*args, **kwargs)
        self.pages = {
            CentralPanelTypes.Initial: CentralWidgets.Init(),
            CentralPanelTypes.RoomSettings: CentralWidgets.RoomSettings(default_settings=RightWidgets.DEFAULT_SETTINGS),
            CentralPanelTypes.ScannerSettings: CentralWidgets.ScannerSettings(),
            CentralPanelTypes.Scanner: CentralWidgets.ScannerControl(),
            CentralPanelTypes.Test: CentralWidgets.Test(),
        }
        self.stacked_widget = QStackedWidget(self)
        for key in self.pages.keys():
            self.stacked_widget.insertWidget(key, self.pages[key])  # добавление виджетов в центральную панель

        self.setWidget(self.stacked_widget)
        self.setWidgetResizable(True)

    def display(self, i):
        self.stacked_widget.setCurrentIndex(i)


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
                '%(asctime)s %(levelname)s: %(message)s')
        )

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
        room_settings: CentralWidgets.RoomSettings = self.center_panel.pages[CentralPanelTypes.RoomSettings]
        self.right_panel = RightPanel(self.main_widget)  # graphics
        self.log_panel = LogPanel(self.main_widget)  # log window

        self.left_panel.leftlist.currentRowChanged.connect(self.center_panel.display)
        room_settings.settings_signal.connect(self.right_panel.scanner_widget.set_settings_from_dict)

        left_center_splitter = QSplitter(orientation=Qt.Orientation.Horizontal)
        left_center_splitter.insertWidget(0, self.left_panel)
        left_center_splitter.insertWidget(1, self.center_panel)
        left_center_splitter.setStretchFactor(0, 0)
        left_center_splitter.setStretchFactor(1, 1)
        left_center_splitter.setCollapsible(0, False)
        left_center_splitter.setCollapsible(1, False)

        log_splitter = QSplitter(orientation=Qt.Orientation.Vertical)
        log_splitter.insertWidget(0, left_center_splitter)
        log_splitter.insertWidget(1, self.log_panel)
        log_splitter.setStretchFactor(0, 4)
        log_splitter.setStretchFactor(1, 1)
        log_splitter.setCollapsible(0, False)
        log_splitter.setCollapsible(1, False)

        main_splitter = QSplitter(orientation=Qt.Orientation.Horizontal)
        main_splitter.insertWidget(0, log_splitter)
        main_splitter.insertWidget(1, self.right_panel)

        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 1)
        main_splitter.setCollapsible(0, False)
        main_splitter.setCollapsible(1, False)

        hbox.addWidget(main_splitter)

        self.setGeometry(300, 300, 450, 400)
        self.setWindowTitle('Scanner control')
        self.setCentralWidget(self.main_widget)
