import socket

from typing import List, Union
from ..analyzator_parameters import (
    ResultsFormatType, FrequencyParameters, SParameters, FrequencyTypes
)
from ..base_analyzator import BaseAnalyzator, AnalyzerSignals, AnalyzerConnectionError
from ...utils import EmptySignal
import RsInstrument
import numpy as np


class RohdeSchwarzAnalyzatorSignals(AnalyzerSignals):
    data = EmptySignal()
    is_connected = EmptySignal()


class RohdeSchwarzAnalyzator(BaseAnalyzator):
    def __init__(
            self,
            ip: str,
            port: Union[str, int],
            bufsize: int = 1024,
            maxbufs: int = 1024,
            signals: AnalyzerSignals = None
    ):
        """

        :param ip: ip адрес анализатора
        :param port: порт анализатора
        :param bufsize: размер чанка сообщения в байтах
        :param maxbufs: максимальное число чанков
        """
        self.ip, self.port, self.conn = ip, port, socket.socket()
        self.bufsize, self.maxbufs = bufsize, maxbufs
        self._is_connected = False
        self.instrument = None
        self.settings = None

        if signals is None:
            self._signals = RohdeSchwarzAnalyzatorSignals()
        else:
            self._signals = signals

    def _send_cmd(self, cmd: str):
        if '?' in cmd:
            return self.instrument.queue_str_with_opc(cmd)
        else:
            self.instrument.write_str_with_opc(cmd)

    def set_settings(
            self,
            channel: int,
            settings: FrequencyParameters
    ) -> None:
        self._send_cmd(f'SENSe{channel}:FREQuency:STARt {settings.start}{settings.frequency_type}')
        self._send_cmd(f'SENSe{channel}:FREQuency:STOP {settings.stop}{settings.frequency_type}')
        self._send_cmd(f'SENSe{channel}:SWEep:POINts {settings.num_points}')
        self.settings = settings

    def _set_is_connected(self, state: bool):
        self._is_connected = state

    def connect(self) -> None:
        if self._is_connected:
            return
        resource = f'TCPIP::{self.ip}::{self.port}::SOCKET'
        self.instrument = RsInstrument.RsInstrument(resource, True, True, "SelectVisa='socket'")
        self._set_is_connected(True)

    def disconnect(self) -> None:
        if not self._is_connected:
            return
        try:
            self.instrument.close()
        except Exception as e:
            raise e
        finally:
            self._set_is_connected(False)

    def get_scattering_parameters(
            self,
            parameters: List[SParameters],
            frequency_parameters: FrequencyParameters,
            results_formats: List[ResultsFormatType]
    ) -> dict[str: List[float]]:

        res = {}

        if not self.is_connected:
            raise AnalyzerConnectionError

        channel = 1
        self.set_settings(channel=channel, settings=frequency_parameters)

        for num, S_param in enumerate(parameters):
            num += 1
            self._send_cmd(f'CALC{channel}:PAR:SDEF "Trc{num}", "{S_param}"')
            trace_data = self._send_cmd(f'CALC{channel}:DATA? FDAT')
            trace_tup = tuple(map(str, trace_data.split(',')))
            res[f'{S_param}'] = np.array(trace_tup).astype(float)

        freq_list = self._send_cmd(f'CALC{channel}:DATA:STIM?')
        freq_tup = tuple(map(str, freq_list.split(',')))
        res[f'f'] = np.array(freq_tup).astype(float)

        self._signals.data.emit((res['f'], *(res[f'{S_param}'] for S_param in parameters)), )
        return res

    def is_connected(self) -> bool:
        return self._is_connected

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass


if __name__ == "__main__":
    analyzator = RohdeSchwarzAnalyzator(
        ip="172.16.22.182",
        port="5025"
    )
    analyzator.connect()

    sp = ['S11', 'S23']
    fp = FrequencyParameters(
        1000, 5000, FrequencyTypes.MHZ, 200
    )
    results = analyzator.get_scattering_parameters(
        sp, fp, [ResultsFormatType.DB, ResultsFormatType.REAL]
    )
    print(results['f'], results['S11'])
