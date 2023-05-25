import socket
import threading
import time

from typing import List, Union
from src.analyzers.base_analyzer import BaseAnalyzer, AnalyzerSignals, AnalyzerConnectionError
from src.utils import EmptySignal
import numpy as np
import logging

logger = logging.getLogger(__name__)


class CeyearAnalyzerSignals(AnalyzerSignals):
    data = EmptySignal()
    is_connected = EmptySignal()


class CeyearAnalyzer(BaseAnalyzer):
    def __init__(
            self,
            ip: str,
            port: Union[str, int],
            buf_size: int = 1024,
            max_bufs: int = 1024,
            signals: AnalyzerSignals = None
    ):
        self.ip, self.port, self.conn = ip, port, socket.socket()
        self.buf_size, self.max_bufs = buf_size, max_bufs
        self.tcp_lock = threading.Lock()

        self._is_connected = False

        if signals is None:
            self._signals = CeyearAnalyzerSignals()
        else:
            self._signals = signals

        self.channel = 1

    def _send_cmd(self, cmd: str):
        try:
            self.conn.sendall(str.encode(cmd+'\n'))
            logger.debug(f">>> {cmd}")
            time.sleep(0.1)
            if '?' in cmd:
                response = bytearray()
                while not response.endswith(b'\n'):
                    chunk = self.conn.recv(self.buf_size)
                    if not chunk:
                        break
                    response += chunk
                return response.decode().rstrip()
        except socket.error as e:
            self._set_is_connected(False)
            raise e

    def set_settings(
            self,
            channel: int = 1,
            sweep_type: str = None,
            freq_start: int = None,
            freq_stop: int = None,
            freq_num: int = None,
            bandwidth: int = None,
            aver_fact: int = None,
            smooth_aper: float = None,
            power: int = None
            ) -> None:

        self.channel = channel
        self._set_sweep_type(sweep_type)
        self._set_bandwidth(bandwidth)
        self._set_freqs(freq_start, freq_stop, freq_num)
        self._set_aver_fact(aver_fact)
        self._set_smooth_apert(smooth_aper)
        self._set_power(power)
        logger.info("Settings have been applied")

    def _set_is_connected(self, state: bool):
        self._is_connected = state
        self._signals.is_connected.emit(state)

    def connect(self) -> None:
        if self._is_connected:
            return
        try:
            self.conn.close()
            self.conn = socket.socket()
            self.conn.connect((self.ip, self.port))
            self._send_cmd("*RST")
            self._set_is_connected(True)
            logger.info('Ceyear is connected and reset')
        except Exception as e:
            self._set_is_connected(False)
            raise e

    def disconnect(self) -> None:
        if not self._is_connected:
            return
        try:
            self.conn.shutdown(socket.SHUT_RDWR)
            self.conn.close()
        except Exception as e:
            raise e
        finally:
            self._set_is_connected(False)
            logger.info('Ceyear is disconnected')

    def _set_channel(self, channel: int = None):
        if channel is not None:
            if isinstance(channel, int):
                self.channel = channel
                logger.debug(f"Channel {channel} is selected")
            else:
                raise TypeError("Channel should be string")

    def _get_traces(self):
        res = self._send_cmd(f"CALCulate{self.channel}:PARameter:CATalog?")
        it = iter(res.split(','))
        traces = {}
        for trace, s_param in zip(it, it):
            traces[trace] = s_param.lower()
        return traces

    def _set_sweep_type(self, sweep_type: str = None):
        if sweep_type is not None:
            if isinstance(sweep_type, str):
                if sweep_type == 'LIN' or sweep_type == 'LOG':
                    self._send_cmd(f'SENS{self.channel}:SWE:TYPE {sweep_type}')
                    logger.debug(f"{sweep_type} sweep type is selected")
                else:
                    raise Exception("Unknown sweep type")
            else:
                raise TypeError("Sweep type should be string")

    def _set_freqs(
            self,
            freq_start: int = None,
            freq_stop: int = None,
            freq_num: int = None,
    ):
        if freq_start is not None:
            if isinstance(freq_stop, int):
                if 100_000 <= freq_start <= 8_500_000_000:
                    self._send_cmd(f'SENS{self.channel}:FREQ:STAR {freq_start}Hz')
                    logger.debug(f"Frequency start {freq_start} is selected")
                else:
                    raise Exception("Start frequency must be from 100 KHz to 8.5 MHz")
            else:
                raise TypeError("Start frequency should be int")
        if freq_stop is not None:
            if isinstance(freq_stop, int):
                if 100_000 <= freq_stop <= 8_500_000_000:
                    self._send_cmd(f'SENS{self.channel}:FREQ:STOP {freq_stop}Hz')
                    logger.debug(f"Frequency stop {freq_stop} is selected")
                else:
                    raise Exception("Stop frequency must be from 100 KHz to 8.5 MHz")
            else:
                raise TypeError("Stop frequency should be int")
        if freq_num is not None:
            if isinstance(freq_num, int):
                if 1 <= freq_num <= 16_001:
                    self._send_cmd(f'SENS{self.channel}:SWE:POIN {freq_num}')
                    logger.debug(f"Number of points {freq_num} is selected")
                else:
                    raise Exception("Number of points must be from 1 to 16 001")
            else:
                raise TypeError("Number of points should be integer")

    def _set_bandwidth(self, bandwidth: int = None):
        if bandwidth is not None:
            if isinstance(bandwidth, int):
                if 1 <= bandwidth <= 40_000:
                    self._send_cmd(f'SENS{self.channel}:BAND {bandwidth}')
                    logger.debug(f"Bandwidth {bandwidth} is selected")
                else:
                    raise Exception("Bandwidth factor must be from 1 Hz to 40 kHz")
            else:
                raise TypeError("Bandwidth should be integer")

    def _set_aver_fact(self, aver_fact: int = None):
        if aver_fact is not None:
            if isinstance(aver_fact, int):
                if 1 <= aver_fact <= 1024:
                    self._send_cmd(f'SENS{self.channel}:AVER:STAT ON')
                    self._send_cmd(f'SENS{self.channel}:AVER:COUN  {aver_fact}')
                    logger.debug(f"Average factor {aver_fact} is selected")
                else:
                    raise Exception("Average factor must be from 1 to 1024")
            else:
                raise TypeError("Average factor should be integer")

    def _set_smooth_apert(self, smooth_apert: float = None):
        if smooth_apert is not None:
            if isinstance(smooth_apert, float):
                if 1 < smooth_apert < 25:
                    self._send_cmd(f'CALC{self.channel}:SMO:STAT ON')
                    self._send_cmd(f'CALC{self.channel}:SMO:APER {smooth_apert}')
                    logger.debug(f"Smoothing aperture {smooth_apert} is selected")
                else:
                    raise Exception("Smoothing aperture must be from 1% to 25%")
            else:
                raise TypeError("Smoothing aperture should be integer")

    def _set_power(self, power: int = None):
        if power is not None:
            if isinstance(power, int):
                if -85 <= power <= 20:
                    number_of_ports = int(self._send_cmd(f'SERV:PORT:COUN?'))
                    for n_port in range(1, number_of_ports + 1):
                        self._send_cmd(f'SOUR{self.channel}:POW{n_port} {power}dBm')
                        logger.debug(f"Power {power} is selected")
                else:
                    raise Exception("Power level must be from -85 dBm to 20 dBm")
            else:
                raise TypeError("Smoothing aperture should be integer")

    def get_scattering_parameters(
            self,
            parameters: List[str],
    ) -> dict[str: List[complex]]:
        if len(parameters) != len(set(parameters)):
            raise ValueError("S-parameters must be unique!")
        parameters = [p.lower() for p in parameters]

        res = {}

        if not self.is_connected:
            raise AnalyzerConnectionError

        freq_data = self._send_cmd(f'SENS{self.channel}:FREQ:DATA?')
        freq_tup = tuple(map(str, freq_data.split(',')))
        res[f'freq'] = np.array(freq_tup).astype(float)

        existed = {}
        traces = self._get_traces()

        for trace, s_param in traces.items():
            if (s_param not in parameters) or (s_param in existed):
                self._send_cmd(f"CALC{self.channel}:PAR:DEL '{trace}'")
            else:
                existed[s_param] = trace

        num = 0
        for s_param in parameters:
            if s_param not in existed:
                while num < 32:
                    num += 1
                    if f'Tr{num}' not in traces:
                        break
                else:
                    raise RuntimeError("Max number of traces has been reached")

                self._send_cmd(f"CALC{self.channel}:PAR:DEF 'Tr{num}',{s_param}")
                existed[s_param] = f'Tr{num}'

        for tr_number in self._send_cmd('DISPlay:WINDow1:CATalog?').split(','):
            self._send_cmd(f"DISPlay:WINDow1:TRACe{tr_number}:DEL")

        for num, s_param in enumerate(parameters):
            num += 1
            self._send_cmd(f"DISPlay:WINDow1:TRACe{num}:FEED '{existed[s_param]}'")

        self._send_cmd(f'SENS{self.channel}:SWEep:MODE HOLD')
        self._send_cmd(f'TRIGger:SEQuence:AVERage ON')
        self._send_cmd(f'TRIGger:SEQuence:SINGle;*OPC?')

        for s_param in parameters:
            self._send_cmd(f"CALC{self.channel}:PAR:SEL '{existed[s_param]}'")
            self._send_cmd(f"DISPlay:WINDow1:TRACe{num}:Y:SCALe:AUTO")
            trace_data = self._send_cmd(f'CALC{self.channel}:DATA? SDATA')
            trace_tup = tuple(map(str, trace_data.split(',')))
            trace_array = np.array(trace_tup).astype(float)
            res[f'{s_param}'] = trace_array[:-1:2] + 1j * trace_array[1::2]
            # self._send_cmd(f"CALC{self.channel}:PAR:DEL 'Tr{num}'")

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
#     analyzer = CeyearAnalyzer(ip="192.168.137.119", port=1024)
#     analyzer.connect()
#     analyzer.set_settings(sweep_type='LIN', freq_start=1000000000, freq_stop=3000000000,
#                           freq_num=200, bandwidth=3000, aver_fact=5, smooth_aper=20, power=5)
#     results = analyzer.get_scattering_parameters(['S22', 'S12', 'S12', 'S12', 'S12', 'S12', 'S12', 'S12', 'S12', 'S12'])
#     print(results['freq'], results['S22'])
