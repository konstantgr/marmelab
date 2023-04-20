from PyQt6.QtWidgets import QHBoxLayout, QSizePolicy, QTreeWidget, QTreeWidgetItem, QMenu
from .BasePanel import BasePanel
from PyQt6.QtWidgets import QWidget
from PyQt6.QtCore import QObject, pyqtBoundSignal, pyqtSignal, Qt, QPoint
from pyqt_app import project, builder
from src.project.Project import PScanner, PAnalyzer
from src.views.View import BaseView
from src.ModelView import ModelView
from typing import Union
from PyQt6.QtGui import QCursor, QAction, QBrush, QColor


class TreeSignal(QObject):
    """
    Сигналы дерева проекта
    """
    tree_num: pyqtBoundSignal = pyqtSignal(int)  # ячейка и номер в дереве


class TreeGroupItem(QTreeWidgetItem):
    """
    Группа, верхний уровень
    """
    def __init__(self, *args, name: str, **kwargs):
        super().__init__(*args, [name], **kwargs)
        self.name = name


class TreeModelViewItem(QTreeWidgetItem):
    """
    Модель и ее единственная вьюшка
    """
    def __init__(self, *args, model_view: ModelView, name: str, tree_num: int, **kwargs):
        super().__init__(*args, [name], **kwargs)
        self.name = name
        self.model_view = model_view
        self.tree_num = tree_num


class TreeModelItem(TreeModelViewItem):
    """
    Модель, у которой несколько вьюшек
    """


class TreeViewItem(TreeModelViewItem):
    """
    Вьюшка какой-то модели
    """


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

        self.current_item = None
        self.current_item_name = None
        self.SELECT_COLOR = QColor(255, 128, 0, 101)

        self.tree = QTreeWidget(self)
        self.tree.setColumnCount(1)
        self.tree.setHeaderLabel('Project')

        self.draw()

        self.tree.itemActivated.connect(self.select_widget)
        self.tree.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.tree.customContextMenuRequested.connect(self.context_menu)

        hbox = QHBoxLayout(self)
        hbox.addWidget(self.tree)
        self.setLayout(hbox)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)

        project.objects.signals.changed.connect(self.draw)
        project.paths.signals.changed.connect(self.draw)
        project.plots.signals.changed.connect(self.draw)
        project.measurands.signals.changed.connect(self.draw)
        project.experiments.signals.changed.connect(self.draw)
        project.results.signals.changed.connect(self.draw)

    def draw(self) -> None:
        """
        Отрисовка дерева
        """
        root = self.tree.invisibleRootItem()
        for item in root.takeChildren():
            root.removeChild(item)

        project_tree = builder.model_views
        i = 0
        self.current_item = None
        for group in project_tree.keys():
            group_item = TreeGroupItem(self.tree, name=group.value)
            for element in project_tree[group]:
                views = element.views
                if len(views) == 0:
                    item = TreeModelItem(group_item, model_view=element, name=element.model.name, tree_num=-1)
                    item.setIcon(0, element.icon)
                elif len(views) == 1:
                    item = TreeModelViewItem(group_item, model_view=element, name=views[0].display_name(), tree_num=i)
                    item.setIcon(0, element.icon)
                    if self.current_item_name == item.name:
                        self.current_item = item
                    color = QBrush(self.SELECT_COLOR) if item.name == self.current_item_name else QBrush()
                    item.setBackground(0, color)
                    i += 1
                elif len(views) > 1:
                    item = TreeModelItem(group_item, model_view=element, name=element.model.name, tree_num=-1)
                    item.setIcon(0, element.icon)
                    for view in views:
                        el_item = TreeViewItem(item, model_view=element, name=view.display_name(), tree_num=i)
                        if self.current_item_name == el_item.name:
                            self.current_item = el_item
                        color = QBrush(self.SELECT_COLOR) if el_item.name == self.current_item_name else QBrush()
                        el_item.setBackground(0, color)
                        i += 1

        self.tree.expandAll()

    def select_widget(self, item: Union[TreeGroupItem, TreeModelViewItem, QTreeWidgetItem], column: int) -> None:
        """
        Функция, которая посылает выбранный виджет в сигнал
        """
        if isinstance(item, (TreeViewItem, TreeModelViewItem)):
            self.signals.tree_num.emit(item.tree_num)
            old_item = self.current_item
            if old_item is not None:
                old_item.setBackground(0, QBrush())
            self.current_item = item
            self.current_item_name = item.name
            item.setBackground(0, QBrush(self.SELECT_COLOR))

    def context_menu(self, pos: QPoint):
        item = self.tree.itemAt(pos)
        if isinstance(item, TreeModelViewItem) and not isinstance(item, TreeViewItem):

            menu = QMenu()
            if item.model_view.removable:
                delete_action = QAction("Delete")
                delete_action.triggered.connect(item.model_view.delete)
                menu.addAction(delete_action)
                menu.exec(self.tree.mapToGlobal(pos))
