import socket
import threading

from typing import List, Union
from src.analyzator.analyzator_parameters import (
    AnalyzatorType, ResultsFormatType, FrequencyParameters, SParameters, FrequencyTypes
)
from src.analyzator.base_analyzator import BaseAnalyzator
from RsInstrument import RsInstrument
import numpy as np


class RohdeSchwarzAnalyzator(BaseAnalyzator):
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

    def connect(self) -> None:
        resource = f'TCPIP::{self.ip}::{self.port}::SOCKET'  # VISA resource string for the device
        self.instrument = RsInstrument(resource, True, True, "SelectVisa='socket'")
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

        fr_type = frequency_parameters.frequency_type.value
        res = {}

        if not self.is_connected:
            return

        for num, S_param in enumerate(parameters):
            num += 1
            self.instrument.write(f'CALC{num}:PAR:SDEF "Trc{num}", "{S_param}"')
            self.instrument.write_str(f'SENSe{num}:FREQuency:STARt {frequency_parameters.start}{fr_type}')
            self.instrument.write_str(f'SENSe{num}:FREQuency:STOP {frequency_parameters.stop}{fr_type}')
            self.instrument.write(f'SENSe{num}:SWEep:POINts {frequency_parameters.num_points}')

            self.instrument.write_str(f'CALCulate{num}:PARameter:MEASure "Trc{num}", "{S_param}"')
            trace_data = self.instrument.query_str(f'CALC{num}:DATA? FDAT')
            trace_tup = tuple(map(str, trace_data.split(',')))

            freq_list = self.instrument.query_str(f'CALC{num}:DATA:STIM?')
            freq_tup = tuple(map(str, freq_list.split(',')))

            res[f'{S_param}_freq'] = np.array(freq_tup).astype(float)
            res[f'{S_param}'] = np.array(trace_tup).astype(float)

        return res

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
        sp, fp
    )
    print(results['S11_freq'], results['S11'])
