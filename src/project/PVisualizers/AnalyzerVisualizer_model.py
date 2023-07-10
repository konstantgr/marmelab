from ..Project import PAnalyzerVisualizer, PStorage, PAnalyzerStates, PScanner, PAnalyzer
from ..Worker import Worker
from PyQt6.QtCore import QThreadPool


class PAnalyzerVisualizerModel(PAnalyzerVisualizer):
    def __init__(
            self,
            name: str,
            plots: PStorage,
            scanner: PScanner,
            analyzer: PAnalyzer
    ):
        super(PAnalyzerVisualizerModel, self).__init__(name=name, plots=plots)
        self._thread_pool = QThreadPool()
        self._mstate = True
        self.scanner = scanner
        self.analyzer = analyzer


    # def updater(self):
    #     while bool(self._mstate):
    #         self._widget.current_measurable.measure()
    #
    # def start_worker(self):
    #     if bool(self._mstate):
    #         self._thread_pool.start(Worker(self.updater))
