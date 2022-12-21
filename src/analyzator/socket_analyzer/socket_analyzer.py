import socket
import threading

from typing import List, Union
from src.analyzator.base_analyzator import BaseAnalyzer, AnalyzerSignals, AnalyzerConnectionError
from ...utils import EmptySignal
import numpy as np


class SocketAnalyzerSignals(AnalyzerSignals):
    data = EmptySignal()
    is_connected = EmptySignal()


class SocketAnalyzer(BaseAnalyzer):
    def __init__(
            self,
            ip: str,
            port: Union[str, int],
            bufsize: int = 1024,
            maxbufs: int = 1024,
            signals: AnalyzerSignals = None
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
        self._is_connected = False
        self.instrument = None
        self.channel = 1

        if signals is None:
            self._signals = SocketAnalyzerSignals()
        else:
            self._signals = signals

    def _send_cmd(self, cmd: str):
        self.instrument.send(str.encode(cmd))
        if '?' in cmd:
            # return self.instrument.recv(1024).decode()
            response = bytearray()
            while True:
                chunk = self.instrument.recv(self.bufsize)
                if not chunk:
                    break
                response += chunk
            return response.decode()

    def set_settings(self,
                     channel: int = 1,
                     sweep_type: str = None,
                     freq_start: float = None,
                     freq_stop: float = None,
                     freq_num: int = None,
                     bandwidth: float = None,
                     aver_fact: int = None,
                     smooth_aper: int = None
                     ) -> None:
        self._send_cmd("*RST")
        self.channel = channel
        if sweep_type is not None:
            self._send_cmd(f'SENS{channel}:SWE:TYPE {sweep_type}')
        if bandwidth is not None:
            self._send_cmd(f'SENS{channel}:BAND {bandwidth}')
        if freq_start is not None:
            self._send_cmd(f'SENS{channel}:FREQ:STAR {freq_start}Hz')
        if freq_stop is not None:
            self._send_cmd(f'SENS{channel}:FREQ:STOP {freq_stop}Hz')
        if freq_num is not None:
            self._send_cmd(f'SENS{channel}:SWE:POIN {freq_num}')
        if aver_fact is not None:
            self._send_cmd(f'SENS{channel}:AVER:STAT ON')
            self._send_cmd(f'SENS{channel}:AVER:C {aver_fact}')
        if smooth_aper is not None:
            self._send_cmd(f'CALC{channel}:SMO:STAT ON')
            self._send_cmd(f'CALC{channel}:SMO:APER {smooth_aper}')

    def _set_is_connected(self, state: bool):
        self._is_connected = state
        self._signals.is_connected.emit(state)

    def connect(self) -> None:
        if self._is_connected:
            return
        self.instrument = self.conn
        self.instrument.connect((self.ip, self.port))
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
            parameters: List[str],
    ) -> dict[str: List[complex]]:

        res = {}

        if not self.is_connected:
            raise AnalyzerConnectionError

        for num, s_param in enumerate(parameters):
            num += 1
            self._send_cmd(f'CALC{self.channel}:PAR:DEF "Trc{num}", "{s_param}"')
            self._send_cmd(f'CALC{self.channel}:PAR:SEL "Trc{num}"')
            trace_data = self._send_cmd(f'CALC{self.channel}:DATA? SDATA')
            trace_tup = tuple(map(str, trace_data.split(',')))
            trace_array = np.array(trace_tup).astype(float)
            res[f'{s_param}'] = trace_array[:-1:2] + 1j * trace_array[1::2]

        freq_data = self._send_cmd(f'CALC:DATA:STIM?')  # rsinstrument examples csv
        freq_tup = tuple(map(str, freq_data.split(',')))
        res[f'f'] = np.array(freq_tup).astype(float)

        self._signals.data.emit((res['f'], *(res[f'{s_param}'] for s_param in parameters)), )
        return res

    def is_connected(self) -> bool:
        return self._is_connected

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass


if __name__ == "__main__":
    analyzer = SocketAnalyzer(ip="192.168.5.168", port=9000)
    analyzer.connect()
    analyzer.set_settings(sweep_type='LIN', freq_start=1000000000, freq_stop=3000000000,
                          freq_num=200, bandwidth=3000, aver_fact=5, smooth_aper=20)
    results = analyzer.get_scattering_parameters(['S11', 'S23'])
    print(results['f'], results['S11'])
