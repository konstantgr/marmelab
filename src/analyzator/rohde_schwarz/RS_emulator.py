import socket
import threading

from typing import List, Union
from src.analyzator.analyzator_parameters import (
    AnalyzatorType, ResultsFormatType, FrequencyParameters, SParameters, FrequencyTypes
)
from src.analyzator.base_analyzator import BaseAnalyzator
import numpy as np


class RohdeSchwarzEmulator(BaseAnalyzator):
    analyzator_type = AnalyzatorType.ROHDE_SCHWARZ

    def __init__(
            self,
            ip: str,
            port: Union[str, int],
            bufsize: int = 1024,
            maxbufs: int = 1024,
    ):
        """

        :param ip: ip адрес сканера
        :param port: порт сканера
        :param bufsize: размер чанка сообщения в байтах
        :param maxbufs: максимальное число чанков
        """
        self.ip, self.port, self.conn = ip, port, socket.socket()
        self.bufsize, self.maxbufs = bufsize, maxbufs
        self.tcp_lock = threading.Lock()
        self.is_connected = False
        self.instrument = None
        self.settings = None

    def _send_cmd(self, cmd: str):
        if '?' in cmd:
            return self.instrument.queue_str_with_opc(cmd)
        else:
            self.instrument.write_str_with_opc(cmd)

    def set_settings(self, channel: int, settings: FrequencyParameters) -> None:
        self.settings = settings

    def connect(self) -> None:
        self.is_connected = True

    def disconnect(self) -> None:
        if not self.is_connected:
            return
        try:
            self.is_connected = False
        except Exception as e:
            return

    def get_scattering_parameters(
            self,
            parameters: List[SParameters],
            frequency_parameters: FrequencyParameters,
            results_formats: List[ResultsFormatType]
    ) -> dict[str: List[float]]:

        res = {}

        if not self.is_connected:
            return

        channel = 1
        self.set_settings(channel=channel, settings=frequency_parameters)

        freq_tup = tuple(np.zeros(frequency_parameters.num_points))
        res[f'f'] = np.array(freq_tup).astype(float)

        for num, S_param in enumerate(parameters):
            trace_tup = tuple(np.zeros(frequency_parameters.num_points))
            res[f'{S_param}'] = np.array(trace_tup).astype(float)

        return res

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass


if __name__ == "__main__":
    analyzator = RohdeSchwarzEmulator(
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
