from PyQt6.QtWidgets import QListWidget, QHBoxLayout, QSizePolicy, QTreeView, QWidget, QTreeWidget, QTreeWidgetItem
from .BasePanel import BasePanel
from .CentralPanel import CentralPanelTypes


class LeftPanel(BasePanel):
    """
    This class makes widgets on the left panel
    """
    def __init__(self, *args, **kwargs):
        """
        Формирование стеков виджетов на левой панели
        """
        super().__init__(*args, **kwargs)


        # self.tree_widget = QTreeWidget()
        # self.tree_widget.setColumnCount(2)
        # self.panels = ["Analyser", "Scanner", "Test"]
        # self.pgs = {"Analyser": [CentralPanelTypes.RoomSettings, CentralPanelTypes.Initial],
        #             "Scanner": [CentralPanelTypes.ScannerSettings, CentralPanelTypes.Scanner],
        #             "Test": ["CentralPanelTypes.Test"]}
        #
        # for i in self.panels:
        #     panels_item = QTreeWidgetItem(self.tree_widget)
        #     panels_item.setText(0, i)
        #
        #     for j in self.pgs[i]:
        #         pages_item = QTreeWidgetItem(self.tree_widget)
        #
        #         #pages_item.setText(0, j)
        #         panels_item.addChild(pages_item)
        #
        #
        #
        #
        # hbox = QHBoxLayout(self)
        # hbox.addWidget(self.tree_widget)
        #
        # self.setLayout(hbox)
        # self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)

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

