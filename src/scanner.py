"""
Базовые классы для управления сканером
"""
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass


class ScannerConnectionError(Exception):
    """
    Исключение, вызываемое при проблеме с подключением: разрыв соединения, невозможность подключиться, таймаут
    """
    pass


class ScannerInternalError(Exception):
    """
    Исключение, вызываемое при проблеме в самом сканере: неправильная команда, достижение предела по одной из координат
    """
    def __init__(self, message):
        super().__init__(message)


@dataclass
class BaseAxes:
    """
    Все координаты сканера
    """
    x: float = None
    y: float = None
    z: float = None
    w: float = None
    # e: float = None
    # f: float = None
    # g: float = None

    def to_dict(self) -> dict[str:float]:
        """
        Перевод датакласса в словарь

        :return:
        """
        return {
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'w': self.w,
            # 'e': self.e,
            # 'f': self.f,
            # 'g': self.g,
        }


@dataclass
class Position(BaseAxes):
    """
    Координаты каждой оси
    """


@dataclass
class Velocity(BaseAxes):
    """
    Скорости каждой оси
    """


@dataclass
class Acceleration(BaseAxes):
    """
    Ускорения каждой оси
    """


@dataclass
class Deceleration(BaseAxes):
    """
    Замедления каждой оси
    """


class Scanner(metaclass=ABCMeta):
    """
    Базовый класс сканера
    """

    @abstractmethod
    def goto(self, position: Position) -> None:
        """
        Переместиться в точку point

        :param position: то, куда необходимо переместиться
        :type position: Position
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
    def position(self) -> Position:
        """
        Позиция сканера

        :return:
        :rtype: Position
        """
        return None

    @property
    @abstractmethod
    def velocity(self) -> Velocity:
        """
        Скорость сканера

        :return:
        :rtype: Velocity
        """
        return None

    @property
    @abstractmethod
    def acceleration(self) -> Acceleration:
        """
        Ускорения сканера

        :return:
        :rtype: Acceleration
        """
        return None

    @property
    @abstractmethod
    def deceleration(self) -> Deceleration:
        """
        Замедления сканера

        :return:
        :rtype: Deceleration
        """
        return None

    @abstractmethod
    def connect(self) -> None:
        """
        Подключение к сканеру

        :return:
        :rtype:
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

    @abstractmethod
    def debug_info(self) -> str:
        """
        Возвращает максимум информации о сканере

        :return:
        """
        pass


