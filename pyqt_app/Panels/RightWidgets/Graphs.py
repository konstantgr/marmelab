import pandas as pd
from PyQt6.QtWidgets import QWidget, QFrame, QHBoxLayout, QVBoxLayout, QSplitter, QStackedWidget, QSizePolicy
from pyqtgraph import plot, PlotWidget
import pyqtgraph as pg


class GraphWidget(QWidget):
    """
    This class makes widget with graphs data
    """
    def __init__(self, *args, **kwargs):
        super(GraphWidget, self).__init__()
        #  добавить дефолтные настройки
        self.vbox = QVBoxLayout(self)
        self.setLayout(self.vbox)

        self.graph_widget = PlotWidget()
        self.vbox.addWidget(self.graph_widget)
        self.graph_widget.plot(*self.obained_data())

    def obained_data(self):
        # data = pd.read_excel('data.xlsx', dtype={'X': float, 'Y': float})
        # x = data['X']
        # y = data['Y']
        x = [123, 124]
        y = [3, 4]
        return x, y
