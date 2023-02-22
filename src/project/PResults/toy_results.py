import numpy as np

from typing import Tuple
from pathlib import Path
from ..Project import PResults


class ToyResults(PResults):
    def __init__(self, results: np.ndarray, names: Tuple[str, ...]):
        super(ToyResults, self).__init__(results=results, names=names)
        self.results = results
        self.names = names

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
