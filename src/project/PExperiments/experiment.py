import time

from ..Project import PExperiment, PPath, PMeasurand, PScanner, ProjectType, PStorage
from ..Project import PBaseSignals
from PyQt6.QtCore import pyqtBoundSignal, pyqtSignal, QObject, QThreadPool
from ..Worker import Worker


class ExperimentSignals(PBaseSignals):
    path_changed: pyqtBoundSignal = pyqtSignal()
    measurands_changed: pyqtBoundSignal = pyqtSignal()


class Experiment(PExperiment):
    type_name = 'Experiment'
    signals_type = ExperimentSignals
    signals: ExperimentSignals

    def __init__(self, name: str, paths: PStorage[PPath], measurands: PStorage[PMeasurand], scanner: PScanner):
        super(Experiment, self).__init__(name=name)
        self.thread_pool = QThreadPool()
        self.paths_storage = paths
        self.measurands_storage = measurands
        self.scanner = scanner
        self.current_path: str = ''
        self.current_measurands: list[str] = []
        self.paths_storage.signals.changed.connect(self.on_paths_updated)
        self.measurands_storage.signals.changed.connect(self.on_measurands_updated)

    @property
    def paths(self):
        return self.paths_storage.keys()

    @property
    def measurands(self):
        return self.measurands_storage.keys()

    def run_push(self):
        worker = Worker(self.run)
        self.thread_pool.start(worker)

    def run(self):
        res = None  # сделать переменную рабочей
        model_path = self.paths_storage.get(self.current_path)
        try:
            self.scanner.states.is_in_use.set(True)
            for i in model_path.get_points():
                self.scanner.instrument.goto(i)
                for meas_name in self.current_measurands:
                    res = self.measurands_storage[meas_name].measure()
        except Exception as e:
            raise e
        finally:
            self.scanner.states.is_in_use.set(False)

        print(model_path.get_points())

    @classmethod
    def reproduce(cls, name: str, project: ProjectType) -> 'PBaseTypes':
        return cls(name=name, paths=project.paths, measurands=project.measurands, scanner=project.scanner)

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

