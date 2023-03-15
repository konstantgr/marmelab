from ..Project import PExperiment, PPath, PMeasurand, PScanner, ProjectType, PStorage

class Experiment(PExperiment):
    type_name = 'True\nexperiment'

    def __init__(self, name: str, paths: PStorage[PPath], measurands: PStorage[PMeasurand], scannner: PScanner):
        super(Experiment, self).__init__(name=name)
        self.paths = paths
        self.measurands = measurands
        self.scanner = scannner
        self.current_path: None or str = None
        self.current_measurands: list[str] = []

    def run(self):
        self.paths.data[0].get_points_ndarray()
        self.paths.get(self.current_path)
        self.current_path in self.paths

    @classmethod
    def reproduce(cls, name: str, project: ProjectType) -> 'PBaseTypes':
        pass

