import time
import datetime
import numpy as np
import logging

from ..PResults.toy_results import ToyResults
from ..Project import PExperiment, PPath, PMeasurand, PScanner, ProjectType, PStorage
from ..Project import PBaseSignals
from PyQt6.QtCore import pyqtBoundSignal, pyqtSignal, QObject, QThreadPool
from ..Worker import Worker
from ...builder import FactoryGroups

logger = logging.getLogger(__name__)


class ExperimentSignals(PBaseSignals):
    path_changed: pyqtBoundSignal = pyqtSignal()
    measurands_changed: pyqtBoundSignal = pyqtSignal()
    create_res: pyqtBoundSignal = pyqtSignal()


class Experiment(PExperiment):
    type_name = 'Experiment'
    signals_type = ExperimentSignals
    signals: ExperimentSignals

    def __init__(self,
                 name: str,
                 paths: PStorage[PPath],
                 measurands: PStorage[PMeasurand],
                 scanner: PScanner,
                 app_builder,
                 project: ProjectType):

        super(Experiment, self).__init__(name=name)
        self.thread_pool = QThreadPool()
        self.is_running = False
        self.paths_storage = paths
        self.measurands_storage = measurands
        self.scanner = scanner
        self.app_builder = app_builder
        self.current_path: str = ''
        self.current_measurands: list[str] = []
        self.paths_storage.signals.changed.connect(self.on_paths_updated)
        self.measurands_storage.signals.changed.connect(self.on_measurands_updated)
        self.signals.create_res.connect(self.res_create)
        self.project = project
        self.current_date = datetime.date.today()
        self.is_aborted = False

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
        self.is_running = True
        self.is_aborted = False
        res = None
        model_path = self.paths_storage.get(self.current_path)
        try:
            res_dic = {}

            for meas_name in self.current_measurands:
                self.signals.create_res.emit()
                time.sleep(1.1)
                results: ToyResults = self.project.results.data[-1]
                measurand_names = self.measurands_storage[meas_name].get_measure_names()
                measurand_names = ('x', 'y', 'z', 'w', *measurand_names)
                results.set_names(measurand_names)
                results.set_results(np.empty((0, len(measurand_names)), dtype=object))
                res_dic[meas_name] = results

            self.scanner.states.is_in_use.set(True)
            start_time = time.time()
            points = model_path.get_points()
            for i, point in enumerate(points):
                if self.is_aborted:
                    raise RuntimeError('Experiment aborted')
                self.scanner.instrument.goto(point)
                for meas_name in self.current_measurands:
                    temp = res_dic[meas_name]
                    res = list(self.measurands_storage[meas_name].measure())
                    pos = self.project.scanner.instrument.position()
                    res = [np.full(len(res[0]), pos.x), np.full(len(res[0]), pos.y), np.full(len(res[0]), pos.z), np.full(len(res[0]), pos.w)] + res

                    res = np.array(res, dtype=object)
                    temp.append_data(res.T)
                loop_time = time.time() - start_time
                left_time = (loop_time / (i + 1)) * (len(points) - (i + 1))
                logger.info(f'Time left: {int(left_time // 60)} min {int(left_time % 60)} s')

        except Exception as e:
            raise e
        finally:
            self.is_running = False
            self.scanner.states.is_in_use.set(False)

    def res_create(self):
        factories = self.app_builder.factories.get(FactoryGroups.results)
        print(self.project.results.data)
        factories[0].create(project=self.project)

    @classmethod
    def reproduce(cls, name: str, project: ProjectType) -> 'PBaseTypes':
        return cls(name=name,
                   paths=project.paths,
                   measurands=project.measurands,
                   scanner=project.scanner,
                   app_builder=project.app_builder,
                   project=project)

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

