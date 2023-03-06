import dataclasses
from typing import Type, Union, Tuple
import numpy as np

from src.project.Project import PAnalyzer
from src.project.Project import PAnalyzerSignals
from src.analyzers.ceyear_analyzer.ceyear_analyzer import CeyearAnalyzer
from src.project.Project import PMeasurand


CEYEAR_DEFAULT_SETTINGS = dict(
        channel=1,
        sweep_type='LIN',
        freq_start=100_000,
        freq_stop=8_500_000_000,
        freq_num=201,
        bandwidth=35_000,
        aver_fact=1,
        smooth_apert=2.5,
        power=0)


class CeyearPAnalyzer(PAnalyzer):
    def __init__(self, signals: PAnalyzerSignals, instrument: CeyearAnalyzer):
        super(CeyearPAnalyzer, self).__init__(
            signals=signals,
            instrument=instrument
        )

    @staticmethod
    def get_measurands(self) -> list[Type[PMeasurand]]:
        return [
            SParams,
        ]

    def create_measurand(self, measurand_type: Type[PMeasurand]) -> PMeasurand:
        if measurand_type == SParams:
            measurand = SParams(panalyzer=self)
            return measurand
        else:
            raise TypeError("Unknown measurand")

    def get_scattering_parameters(
            self,
            s_params: list[str]
    ) -> dict[str: list[complex]]:
        return self.instrument.get_scattering_parameters(s_params)


@dataclasses.dataclass
class SParam:
    """Класс S-параметра, который хранит его настройки"""
    enable: bool = False
    name: str = 'S11'


class SParams(PMeasurand):
    def __init__(
            self,
            panalyzer: CeyearPAnalyzer
    ):
        super(SParams, self).__init__(name='S-parameters')
        self.panalyzer = panalyzer

        self.s_size = 2
        self.channel = 1
        self.sweep_type = 'LIN'
        self.freq_start = 100_000
        self.freq_stop = 8_500_000_000
        self.freq_num = 201
        self.bandwidth = 35_000
        self.aver_fact = 1
        self.smooth_apert = 2.5
        self.power = 0

        self.s_params = self._init_s_params()
        self._data: Union[dict[str: list[complex]], None] = None

    def _clear(self):
        self._data = None
        self.panalyzer.current_measurand = None
        self.signals.changed.emit()

    def _init_s_params(self):
        s_params = []
        for i in range(self.s_size):
            for j in range(self.s_size):
                s_params.append(SParam(
                    enable=(i == j == 0),
                    name=f'S{i + 1}{j + 1}'
                ))
        return s_params

    def pre_measure(self):
        self.panalyzer.set_settings(
            measurand=self,
            channel=self.channel,
            sweep_type=self.sweep_type,
            freq_start=self.freq_start,
            freq_stop=self.freq_stop,
            freq_num=self.freq_num,
            bandwidth=self.bandwidth,
            aver_fact=self.aver_fact,
            smooth_aper=self.smooth_apert,
            power=self.power
        )

    def measure(self) -> np.ndarray:
        if self is not self.panalyzer.current_measurand:
            self.pre_measure()
        req = []
        for s_param in self.s_params:
            if s_param.enable:
                req.append(s_param.name)
        self._data = self.panalyzer.get_scattering_parameters(req)
        return np.array(list(self._data.values()))

    def get_measure_names(self) -> Tuple[str]:
        return tuple(["freq"] + [s_param.name for s_param in self.s_params])

    def get_data(self) -> Union[None, np.ndarray]:
        if self._data is not None:
            return np.array(list(self._data.values()))
        else:
            return None

    def set_s_param(
            self,
            index: int,
            enable: bool = None,
            name: str = None,
    ):
        if enable is not None:
            self.s_params[index].enable = enable
        if name is not None:
            self.s_params[index].name = name
        self._clear()

    def set_channel(self, channel: int = None):
        self.channel = channel
        self._clear()

    def set_sweep_type(self, sweep_type: str = None):
        self.sweep_type = sweep_type
        self._clear()

    def set_freqs(
            self,
            freq_start: float = None,
            freq_stop: float = None,
            freq_num: int = None,
    ):
        self.freq_start = freq_start
        self.freq_stop = freq_stop
        self.freq_num = freq_num
        self._clear()

    def set_bandwidth(self, bandwidth: int = None):
        self.bandwidth = bandwidth
        self._clear()

    def set_aver_fact(self, aver_fact: int = None):
        self.aver_fact = aver_fact
        self._clear()

    def set_smooth_apert(self, smooth_apert: float = None):
        self.smooth_apert = smooth_apert
        self._clear()

    def set_power(self, power: int = None):
        self.power = power
        self._clear()
