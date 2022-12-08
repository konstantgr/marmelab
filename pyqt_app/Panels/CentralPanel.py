from enum import IntEnum, auto
from PyQt6.QtWidgets import QScrollArea, QStackedWidget
from .BasePanel import BasePanel
from .. import Visualizers
from . import CentralWidgets


class CentralPanelTypes(IntEnum):
    """
    замена цифр на названия
    """
    Initial: int = auto()
    RoomSettings = auto()
    ScannerSettings: int = auto()
    Scanner: int = auto()
    Test: int = auto()


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
            CentralPanelTypes.RoomSettings: CentralWidgets.RoomSettings(default_settings=Visualizers.DEFAULT_SETTINGS),
            CentralPanelTypes.ScannerSettings: CentralWidgets.ScannerSettings(),
            CentralPanelTypes.Scanner: CentralWidgets.ScannerControl(),
            CentralPanelTypes.Test: CentralWidgets.Test(),
        }
        self.stacked_widget = QStackedWidget(self)
        for key in self.pages.keys():
            self.stacked_widget.insertWidget(key, self.pages[key])  # добавление виджетов в центральную панель

        self.setWidget(self.stacked_widget)
        self.setWidgetResizable(True)
        self.room_settings: CentralWidgets.RoomSettings = self.pages[CentralPanelTypes.RoomSettings]

    def display(self, i):
        self.stacked_widget.setCurrentIndex(i)