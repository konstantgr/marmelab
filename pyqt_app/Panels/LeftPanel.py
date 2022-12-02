from PyQt6.QtWidgets import QListWidget, QHBoxLayout, QSizePolicy, QTreeView, QWidget, QTreeWidget, QTreeWidgetItem
from PyQt6.QtGui import QStandardItemModel, QStandardItem
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

        """"
        попытка сделать ветвление 
        # tree_view = QTreeView()
        # tree_model = QStandardItemModel()
        # tree_view.setModel(tree_model)
        #
        # # root_node = tree_model.invisibleRootItem()
        # 

        # root_node.appendRow()

        # tw = QTreeWidget()
        # cg = QStandardItem(tw, "Scanner", "Analysator", "Experiment")
        # c1 = QTreeWidgetItem(cg, "Control")
        """

        self.left_widget = QWidget()
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

