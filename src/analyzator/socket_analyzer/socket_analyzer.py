import socket
import threading

from typing import List, Union
from src.analyzator.analyzator_parameters import (
    AnalyzatorType, ResultsFormatType, FrequencyParameters, SParameters, FrequencyTypes
)
from src.analyzator.base_analyzator import BaseAnalyzator
import numpy as np


class SocketAnalyzator(BaseAnalyzator):
    analyzator_type = AnalyzatorType.SOCKET

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
        self.instrument.send(str.encode(cmd))
        if '?' in cmd:
            return self.instrument.recv(1024).decode()

    def set_settings(self, channel: int, settings: FrequencyParameters) -> None:
        self._send_cmd("*RST")
        self._send_cmd(f'SENSe{channel}:FREQuency:STARt {settings.start}{settings.frequency_type}')
        self._send_cmd(f'SENSe{channel}:FREQuency:STOP {settings.stop}{settings.frequency_type}')
        self._send_cmd(f'SENSe{channel}:SWEep:POINts {settings.num_points}')
        self.settings = settings

    def connect(self) -> None:
        self.instrument = self.conn
        self.instrument.connect((self.ip, self.port))
        self.is_connected = True

    def disconnect(self) -> None:
        if not self.is_connected:
            return
        try:
            self.instrument.close()
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

        for num, S_param in enumerate(parameters):
            num += 1
            self._send_cmd(f'CALC{channel}:PAR:DEF "Trc{num}", "{S_param}"')
            self._send_cmd(f'CALC{1}:PAR:SEL "Trc{num}"')
            trace_data = self._send_cmd(f'CALC{channel}:DATA? FDATA')
            trace_tup = tuple(map(str, trace_data.split(',')))
            res[f'{S_param}'] = np.array(trace_tup).astype(float)

        freq_list = self._send_cmd(f'CALC{channel}:DATA:STIM?')
        freq_tup = tuple(map(str, freq_list.split(',')))
        res[f'f'] = np.array(freq_tup).astype(float)
        return res

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass


if __name__ == "__main__":
    analyzator = SocketAnalyzator(
        ip="192.168.5.168",
        port=9000
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