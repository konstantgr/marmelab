from enum import IntEnum, auto
from PyQt6.QtWidgets import QScrollArea, QStackedWidget
from .BasePanel import BasePanel
from . import RightWidgets
from . import CentralWidgets
from PyQt6 import QtWidgets

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
            CentralPanelTypes.RoomSettings: CentralWidgets.RoomSettings(default_settings=RightWidgets.DEFAULT_SETTINGS),
            CentralPanelTypes.ScannerSettings: CentralWidgets.ScannerSettings(),
            CentralPanelTypes.Scanner: CentralWidgets.ScannerControl(),
            CentralPanelTypes.Test: CentralWidgets.Test(),
        }

        self.tree_widget = QtWidgets.QTreeWidget()
        self.tree_widget.setColumnCount(2)



        #self.tree_widget.show()
        self.stacked_widget = QStackedWidget()
        panels = ["Analyser", "Scanner", "Test"]

        for i in panels:
            panels_item = QtWidgets.QTreeWidgetItem(self.tree_widget)
            panels_item.setText(0, i)

            for j in self.pages[i]:
                pages_item = QtWidgets.QTreeWidgetItem(self.tree_widget)
                pages_item.setText(0, j)


        for key in self.pages.keys():
            self.tree_widget.insertTopLevelItems(key, self.pages[key])  # добавление виджетов в центральную панель
            self.stacked_widget.insertWidget(key, self.pages[key])


        self.setWidget(self.tree_widget)
        self.setWidgetResizable(True)
        self.room_settings: CentralWidgets.RoomSettings = self.pages[CentralPanelTypes.RoomSettings]

    def display(self, i):
        self.stacked_widget.setCurrentIndex(i)