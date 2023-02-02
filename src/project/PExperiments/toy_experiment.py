from ..Project import PExperiment, PPath, PMeasurand, PScanner


class ToyExperiment(PExperiment):
    def __init__(self, scanner: PScanner, name: str):
        super(ToyExperiment, self).__init__(name=name)
        self.path: PPath = None
        self.measurands: list[PMeasurand] = []
        self.scanner = scanner

    def set_path(self, path: PPath):
        self.path = path

    def set_measurands(self, measurands: list[PMeasurand]):
        self.measurands = measurands

    def run(self):
        for i in self.path.get_points():
            self.scanner.instrument.goto(i)
            for j in self.measurands:
                j.pre_measure()
                j.measure()

