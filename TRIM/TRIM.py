"""
Реализация управления сканером с контроллером ORBIT/FR AL-4164 и AL-4166
"""
from src import Scanner, BaseAxes, Position, Velocity, Acceleration, Deceleration, ScannerConnectionError, ScannerInternalError
import socket
from typing import Union, List
from dataclasses import dataclass, field


@dataclass
class Axes(BaseAxes):
    """
    Класс, в который добавлены группы A и B
    """
    A: float = None  # all axes
    B: float = None  # X and Y axes

    def to_dict(self) -> dict[str:float]:
        res = super().to_dict()
        res['A'] = self.A
        res['B'] = self.B
        return res


def cmds_from_dict(dct: dict[str:float], basecmd: str, val: bool = True) -> List[str]:
    """
    Переводит словарь {X: V} в 'X<basecmd>=V', но только если V не None.
    Пример: {'x': 100, 'y': None} при basecmd='PS' получаем ['XPS=100']

    :param dct:
    :param basecmd:
    :param val:
    :return:
    """
    cmds = []
    for axis, value in dct.items():
        if value is not None:
            if val:
                cmds.append(f'{axis.upper()}{basecmd}={int(value)}')
            else:
                cmds.append(f'{axis.upper()}{basecmd}')
    return cmds


@dataclass
class AxesSettings:
    """
    Класс с настройками осей
    """
    velocity: Velocity = field(default_factory=Velocity)
    acceleration: Acceleration = field(default_factory=Acceleration)
    deceleration: Deceleration = field(default_factory=Deceleration)

    motor_on: Axes = field(default_factory=Axes)
    motion_mode: Axes = field(default_factory=Axes)
    special_motion_mode: Axes = field(default_factory=Axes)

    def to_cmds(self) -> List[str]:
        cmds = []
        cmds += cmds_from_dict(self.velocity.to_dict(), basecmd='SP')
        cmds += cmds_from_dict(self.acceleration.to_dict(), basecmd='AC')
        cmds += cmds_from_dict(self.deceleration.to_dict(), basecmd='DC')
        cmds += cmds_from_dict(self.motion_mode.to_dict(), basecmd='MM')
        cmds += cmds_from_dict(self.special_motion_mode.to_dict(), basecmd='SM')
        cmds += cmds_from_dict(self.motor_on.to_dict(), basecmd='MO')
        return cmds


DEFAULT_SETTINGS = AxesSettings(
    acceleration=Acceleration(
        x=800000,
        y=1000000,
        z=200000,
        w=2000),
    deceleration=Deceleration(
        x=800000,
        y=1000000,
        z=200000,
        w=2000),
    velocity=Velocity(
        x=1228800,
        y=1024000,
        z=100000,
        w=3000),
    motion_mode=Axes(
        A=1),
    special_motion_mode=Axes(
        A=0),
    motor_on=Axes(
        A=1)
)


class TRIMScanner(Scanner):
    """
    Класс сканера
    """
    def __init__(
            self,
            ip: str,
            port: Union[str, int],
            timeout: float = 10,
            bufsize: int = 1024,
            maxbufs: int = 1028,
    ):
        self.ip = ip
        self.port = port
        self.conn = socket.socket()
        self.conn.settimeout(timeout)
        self.bufsize = bufsize
        self.maxbufs = maxbufs
        self.is_connected = False

    def connect(self) -> None:
        try:
            self.conn.connect((self.ip, self.port))
            self.is_connected = True
        except OSError as e:
            raise ScannerConnectionError from e

    def disconnect(self) -> None:
        try:
            self.conn.shutdown(socket.SHUT_RDWR)
            self.conn.close()
            self.is_connected = False
        except OSError as e:
            raise ScannerConnectionError from e

    def set_settings(self, settings: AxesSettings) -> None:
        cmds = settings.to_cmds()
        self._send_cmds(cmds)

    def _send_cmds(self, cmds: List[str]) -> str:
        try:
            command = ";\n".join(cmds) + ";\n"
            command_bytes = command.encode('ascii')
            self.conn.sendall(command_bytes)

            response = self.conn.recv(self.bufsize)
            i = 1
            while not response.endswith(b'>'):
                response += self.conn.recv(self.bufsize)
                i += 1
                if i >= self.maxbufs:
                    raise ScannerInternalError(f'maxbufs={self.maxbufs} limit is reached')

            if response.endswith(b'?>'):
                raise ScannerInternalError(
                    f'Scanner response:\n{response.decode()}'
                )

            if not response.startswith(command_bytes):
                raise ScannerInternalError(
                    f'Scanner response:\n{response.decode()}\n\nEcho in start was expected:\n{command}'
                )

            answer = response.decode().removeprefix(command).removesuffix('>')
            return answer
        except OSError or TimeoutError as e:
            raise ScannerConnectionError from e

    def goto(self, position: Position) -> None:
        cmds = cmds_from_dict(position.to_dict(), 'PS')
        cmds += cmds_from_dict(position.to_dict(), 'BG', val=False)
        self._send_cmds(cmds)

    def stop(self) -> None:
        cmds = ['AST']
        self._send_cmds(cmds)

    @property
    def position(self) -> Position:
        res = self._send_cmds(['APS']).split(',')
        ans = Position(
            x=int(res[0]),
            y=int(res[1]),
            z=int(res[2]),
            w=int(res[3]))
        return ans

    @property
    def velocity(self) -> Velocity:
        res = self._send_cmds(['ASP']).split(',')
        ans = Velocity(
            x=int(res[0]),
            y=int(res[1]),
            z=int(res[2]),
            w=int(res[3]))
        return ans

    @property
    def acceleration(self) -> Acceleration:
        res = self._send_cmds(['AAC']).split(',')
        ans = Acceleration(
            x=int(res[0]),
            y=int(res[1]),
            z=int(res[2]),
            w=int(res[3]))
        return ans

    @property
    def deceleration(self) -> Deceleration:
        res = self._send_cmds(['ADC']).split(',')
        ans = Deceleration(
            x=int(res[0]),
            y=int(res[1]),
            z=int(res[2]),
            w=int(res[3]))
        return ans
