import socket
import threading

from typing import List, Union
from analyzator.analyzator_parameters import (
    AnalyzatorType, ResultsFormatType, FrequencyParameters, SParameters,
)
from analyzator.base_analyzator import BaseAnalyzator, AnalyzatorConnectionError


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

    def connect(self) -> None:
        if self.is_connected:
            return
        try:
            self.conn.close()
            self.conn = socket.socket()
            self.conn.connect((self.ip, self.port))
            self.is_connected = True
        except socket.error as e:
            raise AnalyzatorConnectionError from e

    def disconnect(self) -> None:
        if not self.is_connected:
            return
        try:
            self.conn.shutdown(socket.SHUT_RDWR)
            self.conn.close()
        except socket.error:
            self.is_connected = False

    def get_scattering_parameters(
            self,
            parameter: List[SParameters],
            frequency_parameters: FrequencyParameters,
            results_formats: List[ResultsFormatType]
    ) -> dict[str: List[float]]:
        # znb = RsInstrument(resource, True, True, "SelectVisa='rs'")

        # points = 401  # Number of sweep points
        # znb.write_str('SENSe1:FREQuency:STARt 0.01GHZ')  # Start frequency to 10 MHz
        # znb.write_str('SENSe1:FREQuency:STOP 1.0GHZ')  # Stop frequency to 1 GHz
        #
        # znb.write('SENSe1:SWEep:POINts ' + str(points))  # Set number of sweep points to the defined number
        # znb.write_str('CALCulate1:PARameter:MEASure "Trc1", "S21"')  # Measurement now is S21
        # sleep(0.5)  # It will take some time to perform a complete sweep - wait for it

        # points_count = znb.query_int('SENSe1:SWEep:POINts?')  # Request number of frequency points
        # trace_data = znb.query_str('CALC1:DATA? FDAT')  # Get measurement values for complete trace
        # trace_tup = tuple(map(str, trace_data.split(',')))  # Convert the received string into a tuple
        # freq_list = znb.query_str('CALC:DATA:STIM?')  # Get frequency list for complete trace
        # freq_tup = tuple(map(str, freq_list.split(',')))  # Convert the received string into a tuple
        # return {'freq': freq_tup, 'magn': trace_tup}

        return None

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass


if __name__ == "__main__":
    analyzator = RohdeSchwarzAnalyzator(1, 2)

