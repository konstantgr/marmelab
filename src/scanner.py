"""
Базовые классы для управления сканером
"""
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass


@dataclass
class Point:
    """
    Класс точки в пространстве
    """
    x: float or None = None
    y: float or None = None
    z: float or None = None
    w: float or None = None


class Scanner(metaclass=ABCMeta):
    """
    Базовый класс сканера
    """

    @abstractmethod
    def goto(self, point: Point) -> None:
        """
        Переместиться в точку point
        :param point: то, куда необходимо переместиться
        :type point: Point
        :return:
        :rtype:
        """
        pass

    @abstractmethod
    def stop(self) -> None:
        """
        Полная остановка сканера
        :return:
        :rtype:
        """
        pass

    @property
    @abstractmethod
    def current_position(self) -> Point:
        """
        Позиция сканера
        :return:
        :rtype: Point
        """
        return None

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """
        Доступность устройства
        :return:
        :rtype: bool
        """
        return True

    @abstractmethod
    def connect(self) -> None:
        """
        Подключение к сканеру
        :return:
        :rtype:
        """
        pass

    @abstractmethod
    def reconnect(self) -> None:
        """
        Переподключение к сканеру
        :return:
        :rtype: None
        """
        pass

    @abstractmethod
    def disconnect(self) -> None:
        """
        Отключение от сканера
        :return:
        :rtype:
        """
        pass


