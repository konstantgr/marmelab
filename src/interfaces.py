from abc import ABCMeta, abstractmethod
import socket

class Interface(metaclass=ABCMeta):
    """
    Базовый класс интерфеса управления прибором
    """
    @abstractmethod
    def connect(self):
        """
        Подключение интерфейса
        :return:
        :rtype:
        """
        pass

    @abstractmethod
    def send(self, cmd: str):
        """
        Отправить команду cmd
        :param cmd:
        :type cmd:
        :return:
        :rtype:
        """

    @abstractmethod
    def read(self) -> bytes:
        """
        Принять данные
        :return:
        :rtype:
        """


class TCPInterface(Interface):
    """
    Реализация TCP протокола
    """
    def __init__(self, ip: str, port: str or int):
        self.ip = ip
        self.port = port
        self.conn = socket.socket()

    def connect(self):
        """
        Установка соеденения
        :return:
        :rtype:
        """
        self.conn.connect((self.ip, self.port))

    # def send(self, msg: ):
    #     self.conn.send(cmd)

