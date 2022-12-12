from PyQt6.QtWidgets import QHBoxLayout, QSizePolicy, QTreeWidget, QTreeWidgetItem
from .BasePanel import BasePanel
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QObject, pyqtBoundSignal, pyqtSignal
from pyqt_app import project
from src.project import PWidget


class TreeSignal(QObject):
    """
    Сигналы дерева проекта
    """
    tree_num: pyqtBoundSignal = pyqtSignal(int)  # ячейка и номер в дереве


class TreeItem(QTreeWidgetItem):
    """
    Сущность из дерева, содержащая PWidget
    """
    def __init__(self, *args, pwidget: PWidget, tree_num: int, **kwargs):
        super(TreeItem, self).__init__(*args, [pwidget.name], **kwargs)
        self.pwidget = pwidget
        self.tree_num = tree_num


class LeftPanel(BasePanel):
    """
    This class makes widgets on the left panel
    """
    def __init__(self, *args, **kwargs):
        """
        Формирование стеков виджетов на левой панели
        """
        super().__init__(*args, **kwargs)
        self.signals = TreeSignal()
        self.tree = QTreeWidget(self)
        self.tree.setColumnCount(1)
        self.tree.setHeaderLabel('Project')

        self.draw()

        self.tree.itemClicked.connect(self.select_widget)

        hbox = QHBoxLayout(self)
        hbox.addWidget(self.tree)
        self.setLayout(hbox)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)

    def draw(self) -> None:
        """
        Отрисовка дерева
        """
        root = self.tree.invisibleRootItem()
        for item in root.takeChildren():
            root.removeChild(item)

        project_tree = project.tree()
        i = 0
        for tab in project_tree.keys():
            tab_item = QTreeWidgetItem(self.tree, [tab])
            for pwidget in project_tree[tab]:
                item = TreeItem(tab_item, pwidget=pwidget, tree_num=i)
                if pwidget.icon is not None:
                    item.setIcon(0, pwidget.icon)
                i += 1

        self.tree.expandAll()

    def select_widget(self, item: TreeItem or QTreeWidgetItem, column: int) -> None:
        """
        Функция, которая посылает выбранный виджет в сигнал
        """
        if isinstance(item, TreeItem):
            self.signals.tree_num.emit(item.tree_num)
