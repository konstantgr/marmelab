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
        self.vbox.addWidget(self.scanner_widget)

        self.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Preferred)

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

        splitter2 = QSplitter(orientation=Qt.Orientation.Horizontal)
        splitter2.insertWidget(0, self.left_panel)
        splitter2.insertWidget(1, self.center_panel)
        splitter2.setStretchFactor(0, 0)
        splitter2.setStretchFactor(1, 1)
        splitter2.setCollapsible(0, False)
        splitter2.setCollapsible(1, False)

        splitter1 = QSplitter(orientation=Qt.Orientation.Vertical)
        splitter1.insertWidget(0, splitter2)
        splitter1.insertWidget(1, self.log_panel)
        splitter1.setStretchFactor(0, 4)
        splitter1.setStretchFactor(1, 1)
        splitter1.setCollapsible(0, False)
        splitter1.setCollapsible(1, False)

        splitter0 = QSplitter(orientation=Qt.Orientation.Horizontal)
        splitter0.insertWidget(0, splitter1)
        splitter0.insertWidget(1, self.right_panel)
        splitter0.setStretchFactor(0, 1)
        splitter0.setStretchFactor(1, 10)
        splitter0.setCollapsible(0, False)
        splitter0.setCollapsible(1, False)

        hbox.addWidget(splitter0)

        self.setGeometry(300, 300, 450, 400)
        self.setWindowTitle('Scanner control')
        self.setCentralWidget(self.main_widget)
