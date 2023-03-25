import dataclasses
from typing import Type, Union, Tuple
import numpy as np

from src.project.Project import PAnalyzer
from src.project.Project import PAnalyzerSignals
from src.analyzers.ceyear_analyzer.ceyear_analyzer import CeyearAnalyzer
from src.project.Project import PMeasurand, PMeasurandType


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


@dataclasses.dataclass
class SParam:
    """Класс S-параметра, который хранит его настройки"""
    enable: bool = False
    name: str = 'S11'


class SParams(PMeasurand):
    def __init__(
            self,
            analyzer: CeyearAnalyzer
    ):
        super(SParams, self).__init__(name='S-parameters')
        self.analyzer = analyzer
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
        self.s_params = self.init_sparams(self.s_size)
        self._data = None

        self.signals.changed.connect(self.pre_measure)

    @staticmethod
    def init_sparams(s_size):
        s_params = []
        for i in range(s_size):
            for j in range(s_size):
                s_params.append(SParam(
                    enable=(i == j == 0),
                    name=f'S{i + 1}{j + 1}'
                ))
        return s_params

    def pre_measure(self):
        self.analyzer.set_settings(
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
        return self

    def measure(self) -> np.ndarray:
        req = []
        for s_param in self.s_params:
            if s_param.enable:
                req.append(s_param.name)
        self._data = self.analyzer.get_scattering_parameters(req)
        return np.array(list(self._data.values()))

    def get_measure_names(self) -> Tuple[str, ...]:
        return tuple([s_param.name for s_param in self.s_params])

    def get_data(self) -> Union[None, np.ndarray]:
        return np.array(list(self._data.values()))

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

    def set_channel(self, channel: int = None):
        if channel is not None:
            if isinstance(channel, int):
                self.channel = channel
                self.signals.changed.emit()
            else:
                raise TypeError("Channel should be string")

    def set_sweep_type(self, sweep_type: str = None):
        if sweep_type is not None:
            if isinstance(sweep_type, str):
                if sweep_type == 'LIN' or sweep_type == 'LOG':
                    self.sweep_type = sweep_type
                    self.signals.changed.emit()
                else:
                    raise Exception("Unknown sweep type")
            else:
                raise TypeError("Sweep type should be string")

    def set_freqs(
            self,
            freq_start: float = None,
            freq_stop: float = None,
            freq_num: int = None,
    ):
        if freq_start is not None:
            if isinstance(freq_stop, float):
                if 100_000 <= freq_start <= 8_500_000_000:
                    self.freq_start = freq_start
                    self.signals.changed.emit()
                else:
                    raise Exception("Stop frequency must be from 100 KHz to 8.5 MHz")
            else:
                raise TypeError("Start frequency should be float")
        if freq_stop is not None:
            if isinstance(freq_stop, float):
                if 100_000 <= freq_stop <= 8_500_000_000:
                    self.freq_stop = freq_stop
                    self.signals.changed.emit()
                else:
                    raise Exception("Start frequency must be from 100 KHz to 8.5 MHz")
            else:
                raise TypeError("Stop frequency should be float")
        if freq_num is not None:
            if isinstance(freq_num, int):
                if 1 <= freq_num <= 16_001:
                    self.freq_num = freq_num
                    self.signals.changed.emit()
                else:
                    raise Exception("Number of points must be from 1 to 16 001")
            else:
                raise TypeError("Number of points should be integer")

    def set_bandwidth(self, bandwidth: int = None):
        if bandwidth is not None:
            if isinstance(bandwidth, int):
                if 1 <= bandwidth <= 40_000:
                    self.bandwidth = bandwidth
                    self.signals.changed.emit()
                else:
                    raise Exception("Bandwidth factor must be from 1 Hz to 40 kHz")
            else:
                raise TypeError("Bandwidth should be integer")

    def set_aver_fact(self, aver_fact: int = None):
        if aver_fact is not None:
            if isinstance(aver_fact, int):
                if 1 <= aver_fact <= 1024:
                    self.aver_fact = aver_fact
                    self.signals.changed.emit()
                else:
                    raise Exception("Average factor must be from 1 to 1024")
            else:
                raise TypeError("Average factor should be integer")

    def set_smooth_apert(self, smooth_apert: float = None):
        if smooth_apert is not None:
            if isinstance(smooth_apert, float):
                if 1 < smooth_apert < 25:
                    self.smooth_apert = smooth_apert
                    self.signals.changed.emit()
                else:
                    raise Exception("Smoothing aperture must be from 1% to 25%")
            else:
                raise TypeError("Soothing aperture should be integer")

    def set_power(self, power: int = None):
        if power is not None:
            if isinstance(power, int):
                if -85 <= power <= 20:
                    self.power = power
                    self.signals.changed.emit()
                else:
                    raise Exception("Power level must be from -85 dBm to 20 dBm")
            else:
                raise TypeError("Soothing aperture should be integer")


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

    def create_measurand(self, measurand_type: PMeasurandType) -> PMeasurand:
        if measurand_type == SParams:
            measurand = SParams(analyzer=self.instrument)
            return measurand
        else:
            raise Exception("Unknown measurand")
