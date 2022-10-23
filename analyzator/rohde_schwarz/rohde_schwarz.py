import socket
import threading

from typing import List, Union
from analyzator.analyzator_parameters import AnalyzatorType, ResultsFormatType, FrequencyParameters, SParameters
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
        self.ip = ip
        self.port = port
        self.conn = socket.socket()
        self.bufsize = bufsize
        self.maxbufs = maxbufs
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
        return {'a': [0.0]}

    def __enter__(self):
        pass

    def __exit__(self, type, value, traceback):
        pass


if __name__ == "__main__":
    analyzator = RohdeSchwarzAnalyzator(1, 2)

