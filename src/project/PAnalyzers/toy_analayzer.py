from typing import Union, Tuple

import numpy as np

from ..Project import PAnalyzer
from ..Project import PMeasurand


class ToySparam(PMeasurand):
    def __init__(self):
        super(ToySparam, self).__init__(name="S-param")
        self._data = None

    def pre_measure(self) -> None:
        print("ready for measurements")

    def get_measure_names(self) -> Tuple[str, ...]:
        return "freq", "S11"

    def get_data(self) -> Union[None, np.ndarray]:
        return self._data

    def measure(self) -> np.ndarray:
        freq = np.linspace(0, 10, 1000)
        s_param = np.sin(freq) + np.random.normal(0, 0.1, 1000)
        res = np.zeros((1000, 2))
        res[:, 0] = freq
        res[:, 1] = s_param
        self._data = res
        return self.get_data()
    

class ToyAnalyser(PAnalyzer):
    def get_measurands(self) -> list[PMeasurand]:
        return [ToySparam()]
