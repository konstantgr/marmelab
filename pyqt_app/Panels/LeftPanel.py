from PyQt6.QtWidgets import QHBoxLayout, QSizePolicy, QTreeWidget, QTreeWidgetItem
from .BasePanel import BasePanel
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QObject, pyqtBoundSignal, pyqtSignal
from pyqt_app import project, builder
from src.views.View import BaseView

class TreeSignal(QObject):
    """
    Сигналы дерева проекта
    """
    tree_num: pyqtBoundSignal = pyqtSignal(int)  # ячейка и номер в дереве


class TreeItem(QTreeWidgetItem):
    """
    Сущность из дерева, содержащая PWidget
    """
    def __init__(self, *args, widget: BaseView, tree_num: int, **kwargs):
        super(TreeItem, self).__init__(*args, [widget.display_name()], **kwargs)
        self.widget = widget
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

        project.objects.signals.changed.connect(self.draw)
        project.paths.signals.changed.connect(self.draw)
        project.measurands.signals.changed.connect(self.draw)
        project.experiments.signals.changed.connect(self.draw)

    def draw(self) -> None:
        """
        Отрисовка дерева
        """
        root = self.tree.invisibleRootItem()
        for item in root.takeChildren():
            root.removeChild(item)

        project_tree = builder.tree()
        i = 0
        for tab in project_tree.keys():
            tab_item = QTreeWidgetItem(self.tree, [tab])
            for element in project_tree[tab]:
                if not isinstance(element, list):
                    item = TreeItem(tab_item, widget=element, tree_num=i)
                    i += 1
                else:
                    item = QTreeWidgetItem(tab_item, ['31'])
                    for el in element:
                        TreeItem(item, widget=el, tree_num=i)
                        i += 1
                # if pwidget.icon is not None:
                #     item.setIcon(0, pwidget.icon)

        self.tree.expandAll()

    def select_widget(self, item: TreeItem or QTreeWidgetItem, column: int) -> None:
        """
        Функция, которая посылает выбранный виджет в сигнал
        """
        if isinstance(item, TreeItem):
            self.signals.tree_num.emit(item.tree_num)
