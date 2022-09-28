"""
Реализация управления сканером с контроллером ORBIT/FR AL-4164 и AL-4166
"""
import threading
import time

from src import Scanner, BaseAxes, Position, Velocity, Acceleration, Deceleration
from src import ScannerConnectionError, ScannerInternalError, ScannerMotionError
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


# TODO: поменять cmd_from_dict на cmd_from_axes
def cmds_from_dict(dct: dict[str:float], basecmd: str, val: bool = True) -> List[str]:
    """
    Переводит словарь {X: V} в 'X<basecmd>=V', но только если V не None.
    Пример: {'x': 100, 'y': None} при basecmd='PS' получаем ['XPS=100'].
    Если val=False, то получим команды без '=V': ['XPS']

    :param dct: словарь
    :param basecmd: суффикс команды
    :param val: требуется ли указывать значение в команде
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

EM = [
    'Motion is still active',
    'Normal end-of-motion',
    'Forward limit switch',
    'Reverse limit switch',
    'High software limit',
    'Low software limit',
    'Motor was disabled',
    'User command (stop or abort)',
    'Motor off by user'
]

DEFAULT_SETTINGS = {
    'acceleration': Acceleration(
        x=800000,
        y=1000000,
        z=200000,
        w=2000,
    ),
    'deceleration': Deceleration(
        x=800000,
        y=1000000,
        z=200000,
        w=2000,
    ),
    'velocity': Velocity(
        x=1228800,
        y=1024000,
        z=100000,
        w=3000,
    ),
    'motion_mode': Axes(
        A=0,
    ),
    'special_motion_mode': Axes(
        A=0,
    ),
    'motor_on': Axes(
        A=1,
    )
}


PTP_MODE_SETTINGS = {
    'motion_mode':Axes(
        A=0,
    ),
    'special_motion_mode': Axes(
        A=0,
    ),
    'motor_on': Axes(
        A=1,
    )
}

JOG_MODE_SETTINGS = {
    'motion_mode': Axes(
        A=1,
    ),
    'special_motion_mode': Axes(
        A=0,
    ),
    'motor_on': Axes(
        A=1,
    )
}


class TRIMScanner(Scanner):
    """
    Класс сканера
    """
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
            raise ScannerConnectionError from e

    def disconnect(self) -> None:
        try:
            self.conn.shutdown(socket.SHUT_RDWR)
            self.conn.close()
            self.is_connected = False
        except socket.error as e:
            raise ScannerConnectionError from e

    def set_settings(
            self,
            velocity: Velocity = None,
            acceleration: Acceleration = None,
            deceleration: Deceleration = None,
            motor_on: Axes = None,
            motion_mode: Axes = None,
            special_motion_mode: Axes = None,

    ) -> None:
        """
        Применить настройки

        :param velocity: скорость
        :param acceleration: ускорение
        :param deceleration: замедление
        :param motor_on: включить двигатели
        :param motion_mode: режим работы двигателей
        :param special_motion_mode: подрежим работы двигателей
        :return:
        """
        cmds = []
        if velocity is not None:
            cmds += cmds_from_dict(velocity.to_dict(), basecmd='SP')
        if acceleration is not None:
            cmds += cmds_from_dict(acceleration.to_dict(), basecmd='AC')
        if deceleration is not None:
            cmds += cmds_from_dict(deceleration.to_dict(), basecmd='DC')
        if motion_mode is not None:
            cmds += cmds_from_dict(motion_mode.to_dict(), basecmd='MM')
        if special_motion_mode is not None:
            cmds += cmds_from_dict(special_motion_mode.to_dict(), basecmd='SM')
        if motor_on is not None:
            cmds += cmds_from_dict(motor_on.to_dict(), basecmd='MO')
        self._send_cmds(cmds)

    def _send_cmd(self, cmd: str) -> str:
        """
        Принимает команду, отправляет на сканер и ждет ответа. Ответ возвращает.

        :param cmd: команда
        :return: ответ сканера
        """
        self.tcp_lock.acquire()
        try:
            command = f"{cmd};"
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
                    f'Scanner response:\n{response}'
                )

            if not response.startswith(command_bytes):
                raise ScannerInternalError(
                    f'Scanner response:\n{response}\n\nEcho in start was expected:\n{command}'
                )

            answer = response.decode().removeprefix(command).removesuffix('>')
            return answer
        except socket.error as e:
            self.tcp_lock.release()
            self.is_connected = False
            raise ScannerConnectionError from e
        finally:
            if self.tcp_lock.locked():
                self.tcp_lock.release()

    def _send_cmds(self, cmds: List[str]) -> List[str]:
        """
        Принимает список команд, отправляет их на сканер и ждет все ответы. Ответы возвращает.

        :param cmds: список команд
        :return: ответы на команды
        """
        responses = []
        for cmd in cmds:
            responses.append(self._send_cmd(cmd))
        return responses

    def _is_stopped(self) -> bool:
        """
        Проверяет, остановился ли двигатель

        """
        res = self._send_cmd('AMS').split(',')
        return all([r == '0' for r in res])

    def _end_of_motion_reason(self) -> List[int]:
        """
        Проверка причины остановки

        """
        res = self._send_cmd('AEM').split(',')
        return [int(r) for r in res]

    def goto(self, position: Position) -> None:
        cmds = cmds_from_dict(position.to_dict(), 'AP')
        cmds += cmds_from_dict(position.to_dict(), 'BG', val=False)
        self._send_cmds(cmds)

        while not self._is_stopped():
            time.sleep(0.1)

        stop_reasons = self._end_of_motion_reason()
        if any([r != 1 for r in stop_reasons]):
            raise ScannerMotionError(
                f'During motion to {position} unexpected cause for end-of-motion was received:\n'
                f'\tx: {EM[stop_reasons[0]]}\n'
                f'\ty: {EM[stop_reasons[1]]}\n'
                f'\tz: {EM[stop_reasons[2]]}\n'
                f'\tw: {EM[stop_reasons[3]]}\n'
            )

    def stop(self) -> None:
        self._send_cmd('AST')

    def abort(self) -> None:
        self._send_cmd('AAB')

    def position(self) -> Position:
        res = self._send_cmd('APS').split(',')
        ans = Position(
            x=int(res[0]),
            y=int(res[1]),
            z=int(res[2]),
            w=int(res[3]))
        return ans

    def velocity(self) -> Velocity:
        res = self._send_cmd('ASP').split(',')
        ans = Velocity(
            x=int(res[0]),
            y=int(res[1]),
            z=int(res[2]),
            w=int(res[3]))
        return ans

    def acceleration(self) -> Acceleration:
        res = self._send_cmd('AAC').split(',')
        ans = Acceleration(
            x=int(res[0]),
            y=int(res[1]),
            z=int(res[2]),
            w=int(res[3]))
        return ans

    def deceleration(self) -> Deceleration:
        res = self._send_cmd('ADC').split(',')
        ans = Deceleration(
            x=int(res[0]),
            y=int(res[1]),
            z=int(res[2]),
            w=int(res[3]))
        return ans

    def debug_info(self) -> str:
        cmds = [
            'AAP',  # следующая точка движения в PTP режиме
            'APS',  # актуальные координаты энкотдеров
            # 'APE',
            # 'ADP',
            # 'ARP',
            'AEM',  # причина последней остановки
            'AHL',  # максимальные значения координаты в софте
            'ALL',  # максимальные значения координаты в софте
            'AMM',  # режим движения
            'ASM',  # подрежим движения
            'AMO',  # включен или выключен мотор
            # 'AWW',
            # 'AMF',
            'AMS',  # состояние мотора
        ]
        res = self._send_cmds(cmds)
        return "\n".join([f'{c}: {r}' for c, r in zip(cmds, res)])

    @property
    def is_available(self) -> bool:
        return self.is_connected


# from tests.TRIM_emulator import run
# run(blocking=False)
# sc = TRIMScanner(ip="192.168.5.168", port=9000, )
# sc.connect()
#
# print(sc.velocity())
# print(sc.acceleration())
# print(sc.debug_info())
