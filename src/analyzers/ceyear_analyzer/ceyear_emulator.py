from typing import List, Union
from src.analyzers.base_analyzer import BaseAnalyzer, AnalyzerSignals, AnalyzerConnectionError
from src.utils import EmptySignal
from .ceyear_analyzer import CeyearAnalyzer
import numpy as np
import logging

logger = logging.getLogger(__name__)


class CeyearAnalyzerEmulatorSignals(AnalyzerSignals):
    data = EmptySignal()
    is_connected = EmptySignal()


class CeyearAnalyzerEmulator(CeyearAnalyzer):
    def __init__(
            self,
            ip: str,
            port: Union[str, int],
            bufsize: int = 1024,
            maxbufs: int = 1024,
            signals: AnalyzerSignals = None
    ):
        self._is_connected = False
        self.channel = 1

        if signals is None:
            self._signals = CeyearAnalyzerEmulatorSignals()
        else:
            self._signals = signals

        self._freq_start = None
        self._freq_stop = None
        self._freq_num = None

    def set_settings(self,
                     channel: int = 1,
                     sweep_type: str = None,
                     freq_start: float = None,
                     freq_stop: float = None,
                     freq_num: int = None,
                     bandwidth: int = None,
                     aver_fact: int = None,
                     smooth_aper: float = None,
                     power: int = None
                     ) -> None:
        self.channel = channel
        if freq_start is not None:
            self._freq_start = freq_start
        if freq_stop is not None:
            self._freq_stop = freq_stop
        if freq_num is not None:
            self._freq_num = freq_num
        logger.debug("Settings have been applied")

    def _set_is_connected(self, state: bool):
        self._is_connected = state
        self._signals.is_connected.emit(state)

    def connect(self) -> None:
        if self._is_connected:
            return
        self._set_is_connected(True)
        logger.info('CeyearEmulator is connected')

    def disconnect(self) -> None:
        if not self._is_connected:
            return
        self._set_is_connected(False)
        logger.info('CeyearEmulator is disconnected')

    def get_scattering_parameters(
            self,
            parameters: List[str],
    ) -> dict[str: List[complex]]:

        res = {}

        if not self.is_connected:
            raise AnalyzerConnectionError

        for num, s_param in enumerate(parameters):
            num += 1
            res[f'{s_param}'] = np.random.random(self._freq_num) + 1j * np.random.random(self._freq_num)

        res[f'freq'] = np.linspace(self._freq_start, self._freq_stop, self._freq_num)

        self._signals.data.emit(res)
        logger.debug("S-parameters are received")
        return res

    def is_connected(self) -> bool:
        return self._is_connected

    def __enter__(self):
        self.connect()

    def __exit__(self, exc_type, exc_value, traceback):
        self.disconnect()


# if __name__ == "__main__":
#     analyzer = CeyearAnalyzerEmulator(ip="192.168.137.119", port=1024)
#     analyzer.connect()
#     analyzer.set_settings(sweep_type='LIN', freq_start=1000000000, freq_stop=3000000000,
#                           freq_num=200, bandwidth=3000, aver_fact=5, smooth_aper=20, power=5)
#     results = analyzer.get_scattering_parameters(['S22', 'S12', 'S12', 'S12', 'S12', 'S12', 'S12', 'S12', 'S12', 'S12'])
#     print(results['freq'], results['S22'])