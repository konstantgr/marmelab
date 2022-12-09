from PyQt6.QtWidgets import QScrollArea, QWidget, QStackedWidget
from .BasePanel import BasePanel
from pyqt_app import project


class CentralPanel(QScrollArea, BasePanel):
    """
    This class makes widgets on the central panel
    """
    def __init__(self, *args, **kwargs):
        """
        создание виджетов в центр. панели. В слои они добавляются в классе централ виджет
        """
        super(CentralPanel, self).__init__(*args, **kwargs)

        self.stacked_widget = QStackedWidget(self)

        self.draw()

        self.setWidget(self.stacked_widget)
        self.setWidgetResizable(True)

    def draw(self) -> None:
        """
        Отрисовка всех возможныйх центральных виджетов
        """
        for i in range(self.stacked_widget.count()):
            w = self.stacked_widget.widget(i)
            self.stacked_widget.removeWidget(w)

        project_tree = project.tree()
        i = 0
        for tab in project_tree.keys():
            for pwidget in project_tree[tab]:
                self.stacked_widget.insertWidget(i, pwidget.widget)
                i += 1

    def display(self, tree_num: int) -> None:
        """
        Принимает номер виджета в дереве и выводит его

        :param tree_num:
        :return:
        """
        self.stacked_widget.setCurrentIndex(tree_num)
