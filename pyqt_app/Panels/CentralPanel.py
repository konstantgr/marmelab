from PyQt6.QtWidgets import QScrollArea, QWidget, QStackedWidget, QVBoxLayout, QLabel
from .BasePanel import BasePanel
from pyqt_app import project, builder
from PyQt6.QtGui import QFontDatabase
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

        self.model_names: dict[int: str] = {}
        self.current_element_name = None
        self.main_widget = QWidget()
        self.main_widget.setLayout(QVBoxLayout())

        self.label_widget = QLabel("")
        self.stacked_widget = QStackedWidget(self)

        self.main_widget.layout().addWidget(self.label_widget)
        self.main_widget.layout().addWidget(self.stacked_widget)

        self.empty_widget = QWidget()
        self.empty_widget.setLayout(QVBoxLayout())
        text = QLabel(
            r"""
             __   __  _______  ______    __   __  _______  ___      _______  _______ 
            |  |_|  ||   _   ||    _ |  |  |_|  ||       ||   |    |   _   ||  _    |
            |       ||  |_|  ||   | ||  |       ||    ___||   |    |  |_|  || |_|   |
            |       ||       ||   |_||_ |       ||   |___ |   |    |       ||       |
            |       ||       ||    __  ||       ||    ___||   |___ |       ||  _   | 
            | ||_|| ||   _   ||   |  | || ||_|| ||   |___ |       ||   _   || |_|   |
            |_|   |_||__| |__||___|  |_||_|   |_||_______||_______||__| |__||_______|                                                                                       
            """
        )
        text.setFont(QFontDatabase.systemFont(QFontDatabase.SystemFont.FixedFont))
        self.empty_widget.layout().addWidget(text)

        self.setWidget(self.main_widget)
        self.setWidgetResizable(True)

        self.draw()
        project.objects.signals.changed.connect(self.draw)
        project.paths.signals.changed.connect(self.draw)
        project.plots.signals.changed.connect(self.draw)
        project.measurands.signals.changed.connect(self.draw)
        project.experiments.signals.changed.connect(self.draw)
        project.results.signals.changed.connect(self.draw)

    def draw(self) -> None:
        """
        Отрисовка всех возможныйх центральных виджетов
        """
        for i in range(self.stacked_widget.count()):
            w = self.stacked_widget.widget(i)
            self.stacked_widget.removeWidget(w)

        project_tree = builder.view_tree()
        i = 0
        self.model_names.clear()
        for tab in project_tree.keys():
            for element_name, element in project_tree[tab]:
                if element is None:
                    continue
                elif isinstance(element, BaseView):
                    element.widget.setParent(self.stacked_widget)

                    self.stacked_widget.insertWidget(i, element.widget)
                    self.model_names[i] = element_name
                    i += 1
                elif isinstance(element, list):
                    for el_name, el in element:
                        self.stacked_widget.insertWidget(i, el.widget)
                        self.model_names[i] = el_name
                        i += 1

        self.stacked_widget.addWidget(self.empty_widget)

        for ind, name in self.model_names.items():
            if name == self.current_element_name:
                self.stacked_widget.setCurrentIndex(ind)
                return
        self.display_empty()

    def display(self, tree_num: int) -> None:
        """
        Принимает номер виджета в дереве и выводит его

        :param tree_num:
        :return:
        """
        if self.model_names.get(tree_num) is None:
            self.display_empty()
        else:
            self.stacked_widget.setCurrentIndex(tree_num)
            self.current_element_name = self.model_names.get(tree_num)
            self.label_widget.setText(str(self.current_element_name))

    def display_empty(self):
        self.stacked_widget.setCurrentIndex(self.stacked_widget.count() - 1)
        self.current_element_name = None
        self.label_widget.setText('')
