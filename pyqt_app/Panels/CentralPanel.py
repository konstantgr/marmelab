from PyQt6.QtWidgets import QScrollArea, QWidget, QStackedWidget
from .BasePanel import BasePanel
from pyqt_app import project, builder
from src.views.View import BaseView


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

        project.objects.signals.changed.connect(self.draw)
        project.paths.signals.changed.connect(self.draw)
        project.measurands.signals.changed.connect(self.draw)
        project.experiments.signals.changed.connect(self.draw)

    def draw(self) -> None:
        """
        Отрисовка всех возможныйх центральных виджетов
        """
        for i in range(self.stacked_widget.count()):
            w = self.stacked_widget.widget(i)
            self.stacked_widget.removeWidget(w)

        project_tree = builder.view_tree()
        i = 0
        for tab in project_tree.keys():
            for element_name, element in project_tree[tab]:
                if isinstance(element, BaseView):
                    self.stacked_widget.insertWidget(i, element)
                    i += 1
                elif isinstance(element, list):
                    for el_name, el in element:
                        self.stacked_widget.insertWidget(i, el)
                        i += 1

    def display(self, tree_num: int) -> None:
        """
        Принимает номер виджета в дереве и выводит его

        :param tree_num:
        :return:
        """
        self.stacked_widget.setCurrentIndex(tree_num)
