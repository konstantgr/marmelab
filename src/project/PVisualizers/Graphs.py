from PyQt6.QtWidgets import QWidget, QTabWidget, QLabel, QSizePolicy, QComboBox
from ..Project import PAnalyzerVisualizer, PWidget, PStorage, PAnalyzerStates, PMeasurable
from ..PMeasurables import MeasurableOfMeasurands
from ..Worker import Worker
from PyQt6.QtCore import QThreadPool


class GraphWidget(QTabWidget):
    """
    This class makes widget with graphs data
    """
    def __init__(self, measurables: PStorage[PMeasurable]):
        super(GraphWidget, self).__init__()
        self.measurables = measurables
        self.current_measurable_index = 0
        self._update_current_measurable()

        self._update()
        self.measurables.signals.changed.connect(self._update)
        self.currentChanged.connect(self.set_current_measurable)

    def set_current_measurable(self, index):
        self.current_measurable_index = index
        self._update_current_measurable()

    def _update_current_measurable(self):
        index = self.current_measurable_index
        self.current_measurable = self.measurables.data[index]

    def _update(self):
        self.clear()
        for i, measurable in enumerate(self.measurables.data):
            if measurable.plot_widget is not None:
                self.addTab(measurable.plot_widget, measurable.name)
            else:
                self.addTab(QLabel('No plot'), measurable.name)

            def _on_change(_index, _measurable):
                def _w():
                    self.removeTab(_index)
                    if _measurable.plot_widget is not None:
                        self.insertTab(_index, _measurable.plot_widget, _measurable.name)
                    else:
                        self.insertTab(_index, QLabel('No plot'), _measurable.name)
                    self.setCurrentIndex(_index)
                return _w

            measurable.signals.changed.connect(_on_change(i, measurable))


class PAnalyzerVisualizerRS(PAnalyzerVisualizer):
    def __init__(
            self,
            measurables: PStorage[PMeasurable],
            instrument_states: PAnalyzerStates,
    ):
        super(PAnalyzerVisualizerRS, self).__init__(measurables=measurables)
        self._instrument_states = instrument_states
        self._widget = GraphWidget(measurables=measurables)
        self._control_widgets = []
        self._thread_pool = QThreadPool()

        self._mstate = instrument_states.is_connected & ~instrument_states.is_in_use
        self._mstate.changed_signal.connect(self.start_worker)

    def updater(self):
        while bool(self._mstate):
            self._widget.current_measurable.measure()

    def start_worker(self):
        if bool(self._mstate):
            self._thread_pool.start(Worker(self.updater))

    @property
    def widget(self) -> QWidget:
        return self._widget

    @property
    def control_widgets(self) -> list[PWidget]:
        return self._control_widgets
