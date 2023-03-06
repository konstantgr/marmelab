import numpy as np

from typing import Tuple
from pathlib import Path
from ..Project import PResults


class ToyResults(PResults):
    def __init__(self, name: str):
        super(ToyResults, self).__init__(name=name)
        self.results = None
        self.names = None

    def set_names(self, names: Tuple[str, ...]):
        self.names = names

    def set_results(self, results: np.ndarray):
        self.results = results

    def get_data(self) -> np.ndarray:
        """
        Возвращает все сохраненные данные
        """
        return self.results

    def get_data_names(self) -> Tuple[str, ...]:
        """
        Возвращает названия колонок данных
        """
        return self.names

    def append_data(self, data: np.ndarray):
        """
        Добавить новую строку в результаты
        """
        self.results = np.append(self.results, data, axis=0)

    def to_csv(self, filepath: Path):
        delimiter = ','
        np.savetxt(filepath, self.results, delimiter=delimiter, header=delimiter.join(self.names))

    @classmethod
    def reproduce(cls, name: str, project) -> 'ToyResults':
        return cls(name=name)
