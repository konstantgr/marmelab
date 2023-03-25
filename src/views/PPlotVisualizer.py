from PyQt6.QtWidgets import QWidget, QTabWidget, QLabel, QSizePolicy, QComboBox
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

        self.tab_widget = QTabWidget()
        self.model.plots.signals.changed.connect(self.update_plots)
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
        return self.tab_widget

    def update_plots(self):
        self.tab_widget.clear()
        for plot in self.model.plots.data:
            view = pg.PlotWidget()
            item = pg.PlotDataItem()
            view.addItem(item)
            plot.update()
            item.setData(plot.get_x(), plot.get_f())
            self.tab_widget.addTab(view, plot.name)

