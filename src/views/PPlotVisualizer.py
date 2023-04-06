from PyQt6.QtWidgets import QWidget, QPushButton, QGroupBox, QVBoxLayout, QTabWidget, QLabel, QSizePolicy, QComboBox
from .View import BaseView, QWidgetType
from ..project.PVisualizers.AnalyzerVisualizer_model import PAnalyzerVisualizerModel
from ..project.Project import PPlot1D
import pyqtgraph as pg
from typing import  Union
from functools import partial
import numpy as np


class PlotsView(BaseView[PAnalyzerVisualizerModel]):
    """
    This class makes widget with graphs data
    """
    def __init__(self, *args, **kwargs):
        super(PlotsView, self).__init__(*args, **kwargs)
        self.graphics = []

        self.main_widget = QGroupBox()

        self.tab_widget = QTabWidget()
        self.model.plots.signals.changed.connect(self.update_plots)
        self.main_widget.setLayout(QVBoxLayout())
        self.main_widget.layout().addWidget(self.tab_widget)
        button = QPushButton('Peek')
        button.clicked.connect(self.peek)
        self.main_widget.layout().addWidget(button)

        self.tabs: list[str] = []
        self.current_plot: Union[PPlot1D, None] = None

        # self.tab_widget.currentChanged.connect(self.tab_changed)

    def construct_widget(self) -> QWidgetType:
        self.update_plots()
        return self.main_widget

    def update_plots(self):
        removed = 0
        for i, name in enumerate(self.tabs):
            if name not in self.model.plots.keys():
                self.tab_widget.removeTab(i - removed)
                self.tabs.pop(i - removed)
                removed += 1

        for plot in self.model.plots.data:
            if plot.name in self.tabs:
                continue
            view = pg.PlotWidget()
            item = pg.PlotDataItem()
            view.addItem(item)
            # plot.update()
            plot.signals.current_measurand_measured.connect(partial(self.redraw, len(self.tabs), item))
            # item.setData(plot.get_x(), plot.get_f())
            self.tab_widget.addTab(view, plot.name)
            self.tabs.append(plot.name)

    def _get_current_plot(self):
        current_plot_index = self.tab_widget.currentIndex()
        current_plot_name = self.tab_widget.tabText(current_plot_index)
        current_plot = self.model.plots.get(current_plot_name)
        return current_plot

    def redraw(self, index, item: pg.PlotDataItem):
        if index == self.tab_widget.currentIndex():
            current_plot = self._get_current_plot()
            item.setData(np.abs(current_plot.get_x()), np.abs(current_plot.get_f()))
            # item: pg.PlotDataItem = view.
            # item.setData()

    def peek(self):
        current_plot = self._get_current_plot()
        current_plot.update()
