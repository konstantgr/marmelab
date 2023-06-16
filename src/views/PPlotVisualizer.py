from PyQt6.QtWidgets import QWidget, QPushButton, QGroupBox, QVBoxLayout, QTabWidget, QLabel, QSizePolicy, QComboBox
from .View import BaseView, QWidgetType
from .Widgets import StateDepPushButton
from ..project.PVisualizers.AnalyzerVisualizer_model import PAnalyzerVisualizerModel
from ..project.Project import PPlot1D, PRealTimePlot, PPlot2D
from ..project.PPlots import ResPPlot3DS
import pyqtgraph as pg
from typing import Union
from functools import partial
import numpy as np


class PlotsView(BaseView[PAnalyzerVisualizerModel]):
    """
    This class makes widget with graphs data
    """
    def __init__(self, *args, **kwargs):
        super(PlotsView, self).__init__(*args, **kwargs)
        self.graphics = []
        state_anal = self.model.analyzer.states
        state_scan = self.model.scanner.states
        m_state = ~state_scan.is_in_use & ~state_anal.is_in_use
        self.main_widget = QGroupBox()

        self.tab_widget = QTabWidget()
        self.model.plots.signals.changed.connect(self.update_plots)
        self.main_widget.setLayout(QVBoxLayout())
        self.main_widget.layout().addWidget(self.tab_widget)

        button = StateDepPushButton(
            state=m_state,
            text="Peek",
            parent=self.main_widget
        )
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
            if issubclass(plot.__class__, PPlot2D):
                item = pg.PColorMeshItem()
            elif issubclass(plot.__class__, PPlot1D):
                item = pg.PlotDataItem()

            view.addItem(item)
            # plot.update()
            if issubclass(plot.__class__, PRealTimePlot):
                plot.signals.current_measurand_measured.connect(partial(self.redraw, len(self.tabs), item))
            elif issubclass(plot.__class__, ResPPlot3DS):
                plot.signals.display_changed.connect(partial(self.redraw, len(self.tabs), item))
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
            if isinstance(current_plot, PPlot2D):
                start = 0
                end = 2 * np.pi
                points = 300
                delta = (end - start) / points / 2

                x = np.linspace(start, end, points)
                x_pg = np.linspace(start - delta, end + delta, points + 1)
                y = np.linspace(start, end, points)
                y_pg = np.linspace(start - delta, end + delta, points + 1)

                xx, yy = np.meshgrid(x, y)
                xx_pg, yy_pg = np.meshgrid(x_pg, y_pg)
                item.setData(xx_pg, yy_pg, np.sin(xx**2 + yy**2))

            elif isinstance(current_plot, PPlot1D):
                item.setData(np.abs(current_plot.get_x()), np.abs(current_plot.get_f()))
            # item: pg.PlotDataItem = view.
            # item.setData()

    def peek(self):
        current_plot = self._get_current_plot()
        current_plot.update()
