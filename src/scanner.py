"""
Базовые классы для управления сканером
"""
import dataclasses
from abc import ABCMeta, abstractmethod
from dataclasses import dataclass


class ScannerConnectionError(Exception):
    """
    Исключение, вызываемое при проблеме с подключением: разрыв соединения, невозможность подключиться, таймаут
    """
    def __init__(self):
        super().__init__(
            "Error in scanner connection"
        )


class ScannerInternalError(Exception):
    """
    Исключение, вызываемое при проблеме в самом сканере: неправильная команда, достижение предела по одной из координат
    """
    def __init__(self, message):
        super().__init__(
            f'Scanner error:\n{message}'
        )


class ScannerMotionError(Exception):
    """
    Исключение, поднимаемое при ошибках во время движения сканера
    """
    def __init__(self, message):
        super().__init__(
            f'Scanner motion error:\n{message}'
        )


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

        :return: словарь с названием осей в ключах
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

    def __add__(self, other):
        if isinstance(other, BaseAxes):
            res = BaseAxes(
                *[self.__getattribute__(attr.name) + other.__getattribute__(attr.name) for attr in
                  dataclasses.fields(BaseAxes)]
            )
            return res
        else:
            raise NotImplementedError

    def __sub__(self, other):
        if isinstance(other, BaseAxes):
            res = BaseAxes(
                *[self.__getattribute__(attr.name) - other.__getattribute__(attr.name) for attr in
                  dataclasses.fields(BaseAxes)]
            )
            return res
        else:
            raise NotImplementedError


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
        """

    @abstractmethod
    def stop(self) -> None:
        """
        Полная остановка сканера (сначала замедлится, потом остановится)

        """

    @abstractmethod
    def abort(self) -> None:
        """
        Незамедлительная остановка сканера

        """

    @abstractmethod
    def position(self) -> Position:
        """
        Позиция сканера

        :return: позиция
        """

    @abstractmethod
    def velocity(self) -> Velocity:
        """
        Скорость сканера

        :return: скорость
        """

    @abstractmethod
    def acceleration(self) -> Acceleration:
        """
        Ускорения сканера

        :return: ускорение
        """

    @abstractmethod
    def deceleration(self) -> Deceleration:
        """
        Замедления сканера

        :return: замедление
        """

    @abstractmethod
    def connect(self) -> None:
        """
        Подключение к сканеру

        """

    @abstractmethod
    def disconnect(self) -> None:
        """
        Отключение от сканера

        """

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """
        Доступность сканера для управления

        :return: доступность
        """

    @abstractmethod
    def debug_info(self) -> str:
        """
        Возвращает максимум информации о сканере

        :return: максимальное количество информации о сканере
        """

    @abstractmethod
    def home(self) -> None:
        """
        Перемещение сканера домой и выставление его реального положения

        """
