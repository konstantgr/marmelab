from PyQt6.QtWidgets import QWidget, QPushButton, QGroupBox, QVBoxLayout, QTabWidget, QLabel, QSizePolicy, QComboBox
from .View import BaseView, QWidgetType
from ..project.PVisualizers.AnalyzerVisualizer_model import PAnalyzerVisualizerModel
import pyqtgraph as pg


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
        # self.tab_widget.layout().addWidget()
    #     self.measurables = measurables
    #     self.current_measurable_index = 0
    #     self._update_current_measurable()
    #
    #     self._update()
    #     self.measurables.signals.changed.connect(self._update)
    #     self.currentChanged.connect(self.set_current_measurable)
    #
    # def set_current_measurable(self, index):
    #     self.current_measurable_index = index
    #     self._update_current_measurable()
    #
    # def _update_current_measurable(self):
    #     index = self.current_measurable_index
    #     self.current_measurable = self.measurables.data[index]
    #
    # def _update(self):
    #     self.clear()
    #     for i, measurable in enumerate(self.measurables.data):
    #         if measurable.plot_widget is not None:
    #             self.addTab(measurable.plot_widget, measurable.name)
    #         else:
    #             self.addTab(QLabel('No plot'), measurable.name)
    #
    #         def _on_change(_index, _measurable):
    #             def _w():
    #                 self.removeTab(_index)
    #                 if _measurable.plot_widget is not None:
    #                     self.insertTab(_index, _measurable.plot_widget, _measurable.name)
    #                 else:
    #                     self.insertTab(_index, QLabel('No plot'), _measurable.name)
    #                 self.setCurrentIndex(_index)
    #             return _w
    #
    #         measurable.signals.changed.connect(_on_change(i, measurable))

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
            # item.setData(plot.get_x(), plot.get_f())
            self.tab_widget.addTab(view, plot.name)
            self.tabs.append(plot.name)

    def peek(self):
        current_plot_index = self.tab_widget.currentIndex()
        current_plot_name = self.tab_widget.tabText(current_plot_index)
        current_plot = self.model.plots.get(current_plot_name)
        current_plot.update()