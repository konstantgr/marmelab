from ..Project import PStorage, PExperiment
from ..PObjects import Object3d
from ..PPaths import Path3d
from dataclasses import field


class ObjectsStorage3d(PStorage):
    data: list[Object3d] = field(default_factory=list)


class PathsStorage3d(PStorage):
    data: list[Path3d] = field(default_factory=list)


class ExperimentsStorage(PStorage):
    data: list[PExperiment] = field(default_factory=list)