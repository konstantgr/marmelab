from ..Project import PExperiment, PPath, PMeasurand, PScanner, ProjectType, PStorage
from ..Project import PBaseSignals
from PyQt6.QtCore import pyqtBoundSignal, pyqtSignal, QObject


class ExperimentSignals(PBaseSignals):
    path_changed: pyqtBoundSignal = pyqtSignal()
    measurands_changed: pyqtBoundSignal = pyqtSignal()


class Experiment(PExperiment):
    type_name = 'True\nexperiment'
    signals_type = ExperimentSignals
    signals: ExperimentSignals

    def __init__(self, name: str, paths: PStorage[PPath], measurands: PStorage[PMeasurand], scannner: PScanner):
        super(Experiment, self).__init__(name=name)
        self.paths_storage = paths
        self.measurands_storage = measurands
        self.scanner = scannner
        self.current_path: None or str = None
        self.current_measurands: list[str] = []

    @property
    def paths(self):
        return self.paths_storage.keys()

    @property
    def measurands(self):
        return self.measurands_storage.keys()

    def run(self):
        self.paths.data[0].get_points_ndarray()
        self.paths.get(self.current_path)
        self.current_path in self.paths

    @classmethod
    def reproduce(cls, name: str, project: ProjectType) -> 'PBaseTypes':
        pass

    def on_measurands_updated(self):
        measurands = self.measurands
        self.current_measurands = [i for i in self.current_measurands if i in measurands]
        self.signals.measurands_changed.emit()

    def on_paths_updated(self):
        if self.current_path not in self.paths:
            self.current_path = ''
        self.signals.path_changed.emit()

    def set_current_measurands(self, measurands: list[str]):
        self.current_measurands = measurands

    def set_current_path(self, path: str):
        self.current_path = path
