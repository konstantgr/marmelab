import pandas as pd
from PyQt6.QtWidgets import QWidget, QFrame, QHBoxLayout, QVBoxLayout, QSplitter, QStackedWidget, QSizePolicy
from pyqtgraph import plot, PlotWidget
import pyqtgraph as pg
from ..Project import PAnalyzerVisualizer, PWidget


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
        x = [1, 2, 3]
        y = [1, 4, 9]
        return x, y


class PAnalyzerVisualizerRS(PAnalyzerVisualizer):
    def __init__(self, *args, **kwargs):
        super(PAnalyzerVisualizerRS, self).__init__(*args, **kwargs)
        self._widget = GraphWidget()
        self._control_widgets = []

    @property
    def widget(self) -> QWidget:
        return self._widget

    @property
    def control_widgets(self) -> list[PWidget]:
        return self._control_widgets
