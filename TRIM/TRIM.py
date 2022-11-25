"""
Реализация управления сканером с контроллером ORBIT/FR AL-4164 и AL-4166
"""
import collections
import threading
import time

from src.scanner import Scanner, BaseAxes, Position, Velocity, Acceleration, Deceleration
from src.scanner import ScannerConnectionError, ScannerInternalError, ScannerMotionError
import socket
from typing import Union, List, Iterable
from dataclasses import fields, astuple
from PyQt6.QtCore import pyqtBoundSignal, pyqtSignal, QObject


STEPS_PER_MM_X = 8192
STEPS_PER_MM_Y = 5120
STEPS_PER_MM_Z = 5120
STEPS_PER_DEG_W = 1

AXES_SCALE = BaseAxes(
    x=STEPS_PER_MM_X,
    y=STEPS_PER_MM_Y,
    z=STEPS_PER_MM_Z,
    w=STEPS_PER_DEG_W
)


def cmds_from_axes(axes: BaseAxes, basecmd: str, val: bool = True, scale: bool = True) -> List[str]:
    """
    Переводит BaseAxes(x=V) в 'X<basecmd>=V', но только если V не None.
    Пример: BaseAxes(x=100, y=None) при basecmd='PS' получаем ['XPS=100'].
    Если val=False, то получим команды без '=V': ['XPS']

    :param axes: экземпляр BaseAxes
    :param basecmd: суффикс команды
    :param val: требуется ли указывать значение в команде
    :param scale: требуется ли преобразовать мм в шаги
    :return:
    """
    cmds = []
    for field in fields(axes):
        axis = field.name
        value = axes.__getattribute__(axis)
        scale_val = AXES_SCALE.__getattribute__(axis)
        if value is not None:
            if val:
                cmd_value = int(value * scale_val) if scale else int(value)
                cmds.append(f'{axis.upper()}{basecmd}={cmd_value}')
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


def scanner_motion_error(action_description: str, stop_reasons: List[int]):
    """
    Возвращает исключение по описанию и причинам остановки

    :param action_description: описание движения во время которого возникла ошибка
    :param stop_reasons: причины ошибки (код EM)
    :return:
    """
    return ScannerMotionError(
        f'During {action_description} unexpected cause for end-of-motion was received:\n'
        f'\tx: {EM[stop_reasons[0]]}\n'
        f'\ty: {EM[stop_reasons[1]]}\n'
        f'\tz: {EM[stop_reasons[2]]}\n'
        f'\tw: {EM[stop_reasons[3]]}\n'
    )


DEFAULT_SETTINGS = {
    'acceleration': Acceleration(
        x=800000 / STEPS_PER_MM_X,
        y=1000000 / STEPS_PER_MM_Y,
        z=200000 / STEPS_PER_MM_Z,
        w=2000 / STEPS_PER_DEG_W,
    ),
    'deceleration': Deceleration(
        x=800000 / STEPS_PER_MM_X,
        y=1000000 / STEPS_PER_MM_Y,
        z=200000 / STEPS_PER_MM_Z,
        w=2000 / STEPS_PER_DEG_W,
    ),
    'velocity': Velocity(
        x=1228800 / STEPS_PER_MM_X,
        y=1024000 / STEPS_PER_MM_Y,
        z=100000 / STEPS_PER_MM_Z,
        w=3000 / STEPS_PER_DEG_W,
    ),
    'motion_mode': BaseAxes(
        x=0,
        y=0,
        z=0,
        w=0
    ),
    'special_motion_mode': BaseAxes(
        x=0,
        y=0,
        z=0,
        w=0
    ),
    'motor_on': BaseAxes(
        x=1,
        y=1,
        z=1,
        w=1
    )
}


PTP_MODE_SETTINGS = {
    'motion_mode': BaseAxes(
        x=0,
        y=0,
        z=0,
        w=0
    ),
    'special_motion_mode': BaseAxes(
        x=0,
        y=0,
        z=0,
        w=0
    ),
    'motor_on': BaseAxes(
        x=1,
        y=1,
        z=1,
        w=1
    )
}

JOG_MODE_SETTINGS = {
    'motion_mode': BaseAxes(
        x=1,
        y=1,
        z=1,
        w=1
    ),
    'special_motion_mode': BaseAxes(
        x=0,
        y=0,
        z=0,
        w=0
    ),
    'motor_on': BaseAxes(
        x=1,
        y=1,
        z=1,
        w=1
    )
}


class FIFOLock(object):
    """
    FIFO Lock, который гарантирует поочередное выполнение запросов
    https://gist.github.com/vitaliyp/6d54dd76ca2c3cdfc1149d33007dc34a

    """
    def __init__(self):
        self._lock = threading.Lock()
        self._inner_lock = threading.Lock()
        self._pending_threads = collections.deque()

    def acquire(self, blocking=True):
        with self._inner_lock:
            lock_acquired = self._lock.acquire(False)
            if lock_acquired:
                return True
            elif not blocking:
                return False

            release_event = threading.Event()
            self._pending_threads.append(release_event)

        release_event.wait()
        return self._lock.acquire()

    def release(self):
        with self._inner_lock:
            if self._pending_threads:
                release_event = self._pending_threads.popleft()
                release_event.set()

            self._lock.release()

    def locked(self) -> bool:
        with self._inner_lock:
            return self._lock.locked()

    __enter__ = acquire

    def __exit__(self, t, v, tb):
        self.release()


# убейте меня это какой-то прикол
def _motion_decorator(func):
    """
    Декоратор, который контролирует флаг остановки, потому что это не реализовано в контроллере.
    По документации MS=7 должен об этом сигнализировать, но это не работает.
    Декоратор реализует тред сейф сканера.

    Если в очереди стоят, например goto или home, из разных потоков, то при поднятии _stop_flag, все стоящие в очереди
    команды завершатся.
    После остановки тред с новым движением поменяет _stop_released и _stop_flag.

    :param func:
    """
    def wrapper(self, *args, **kwargs):
        scanner = self  # type: TRIMScanner
        scanner._inner_motion_lock.acquire()
        if scanner._stop_flag and not scanner._stop_released:
            scanner._stop_released = True
            scanner._inner_motion_lock.release()
            with scanner._motion_lock:
                scanner._stop_flag = False
                func(self, *args, **kwargs)
        else:
            scanner._inner_motion_lock.release()
            with scanner._motion_lock:
                if scanner._stop_flag:
                    raise ScannerMotionError(f'During the motion STOP or ABORT was executed')
                func(self, *args, **kwargs)
        if scanner._stop_flag:
            raise ScannerMotionError(f'During the motion STOP or ABORT was executed')
    return wrapper


class ScannerSignals(QObject):
    """
    Класс сигналов для сканера
    """
    position_signal: pyqtBoundSignal = pyqtSignal([BaseAxes], [Position])
    velocity_signal: pyqtBoundSignal = pyqtSignal([BaseAxes], [Velocity])
    acceleration_signal: pyqtBoundSignal = pyqtSignal([BaseAxes], [Acceleration])
    deceleration_signal: pyqtBoundSignal = pyqtSignal([BaseAxes], [Deceleration])


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
        self._tcp_lock = FIFOLock()
        self._motion_lock = FIFOLock()
        self._inner_motion_lock = FIFOLock()
        self._stop_flag = False
        self._stop_released = True
        self.is_connected = False
        self._velocity = Velocity()

        self._signals = ScannerSignals()

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
        if not self.is_connected:
            return
        try:
            self.conn.shutdown(socket.SHUT_RDWR)
            self.conn.close()
            self.is_connected = False
        except socket.error:
            self.is_connected = False

    def set_settings(
            self,
            position: Position = None,
            velocity: Velocity = None,
            acceleration: Acceleration = None,
            deceleration: Deceleration = None,
            motor_on: BaseAxes = None,
            motion_mode: BaseAxes = None,
            special_motion_mode: BaseAxes = None,

    ) -> None:
        """
        Применить настройки

        :param position: положение сканера с энкодеров
        :param velocity: скорость
        :param acceleration: ускорение
        :param deceleration: замедление
        :param motor_on: включить двигатели
        :param motion_mode: режим работы двигателей
        :param special_motion_mode: подрежим работы двигателей
        """
        cmds = []
        if position is not None:
            cmds += cmds_from_axes(position, basecmd='PS')
        if velocity is not None:
            cmds += cmds_from_axes(velocity, basecmd='SP')
        if acceleration is not None:
            cmds += cmds_from_axes(acceleration, basecmd='AC')
        if deceleration is not None:
            cmds += cmds_from_axes(deceleration, basecmd='DC')
        if motion_mode is not None:
            cmds += cmds_from_axes(motion_mode, basecmd='MM', scale=False)
        if special_motion_mode is not None:
            cmds += cmds_from_axes(special_motion_mode, basecmd='SM', scale=False)
        if motor_on is not None:
            cmds += cmds_from_axes(motor_on, basecmd='MO', scale=False)
        self._send_cmds(cmds)
        if position is not None:
            self.position_signal[type(position)].emit(position)
        # Если все прошло успешно, то нужно поменять внутреннюю скорость сканера
        # Это необходимо, так как в самом сканере некорректно реализована команда ASP -- она возвращает нули
        if velocity is not None:
            self.velocity_signal[BaseAxes].emit(velocity)
            for axis in fields(velocity):
                axis_velocity = velocity.__getattribute__(axis.name)
                if axis_velocity is not None:
                    self._velocity.__setattr__(axis.name, axis_velocity)
        if acceleration is not None:
            self.acceleration_signal[type(acceleration)].emit(acceleration)
        if deceleration is not None:
            self.deceleration_signal[type(deceleration)].emit(deceleration)

    def _send_cmd(self, cmd: str) -> str:
        """
        Принимает команду, отправляет на сканер и ждет ответа. Ответ возвращает.

        :param cmd: команда
        :return: ответ сканера
        """
        with self._tcp_lock:
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
                self.is_connected = False
                raise ScannerConnectionError from e

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

    @staticmethod
    def _parse_A_res(res: str, scale=True) -> Union[Iterable[int], Iterable[float]]:
        """
        Принимает строку "1,2,10" и преобразует в кортеж целых чисел (1, 2, 10).
        Если scale=True, переводит шаги в мм и радианы

        :param res: строка целых чисел, разделенных запятой
        :param scale: переводить ли число в мм и радианы
        :return: кортеж
        """
        if not scale:
            return (int(v) for v in res.split(','))
        return (int(v) / axis_scale for v, axis_scale in zip(res.split(','), astuple(AXES_SCALE)))

    def _is_stopped(self) -> bool:
        """
        Проверяет, остановился ли двигатель

        """
        res = self._send_cmd('AMS')
        return all([r == 0 for r in self._parse_A_res(res)])

    def _end_of_motion_reason(self) -> Iterable[int]:
        """
        Проверка причины остановки

        """
        time.sleep(0.02)
        res = self._send_cmd('AEM')
        return self._parse_A_res(res, scale=False)

    def _begin_motion_and_wait(self, cmds, action_description: str = "a motion"):
        """
        Отправляет команды, а затем ждет завершение движения

        :param cmds: команды
        :param action_description: описание движения, которое будет использовано при поднятии исплючения
        """
        self._send_cmds(cmds)

        while not self._is_stopped():
            time.sleep(0.1)

    @_motion_decorator
    def goto(self, position: Position) -> None:
        cmds = cmds_from_axes(position, 'AP')
        cmds += cmds_from_axes(position, 'BG', val=False, scale=False)
        action_description = f'the motion to {position}'
        self._begin_motion_and_wait(cmds, action_description)

        stop_reasons = list(self._end_of_motion_reason())
        if position.x is not None and stop_reasons[0] != 1:
            raise scanner_motion_error(action_description, stop_reasons)
        if position.y is not None and stop_reasons[1] != 1:
            raise scanner_motion_error(action_description, stop_reasons)
        if position.z is not None and stop_reasons[2] != 1:
            raise scanner_motion_error(action_description, stop_reasons)
        if position.w is not None and stop_reasons[3] != 1:
            raise scanner_motion_error(action_description, stop_reasons)

        self.position()

    def stop(self) -> None:
        self._stop_flag = True
        self._stop_released = False
        self._send_cmd('AST')

    def abort(self) -> None:
        self.stop()

    def position(self) -> Position:
        res = self._send_cmd('APS')
        ans = Position(*self._parse_A_res(res))
        self.position_signal.emit(ans)
        return ans

    def _encoder_position(self) -> Position:
        """
        Реальная позиция сканера по положению энкодера

        :return: реальная позиция
        """
        res = self._send_cmd('PS')
        ans = Position(*self._parse_A_res(res))
        return ans

    def velocity(self) -> Velocity:
        self.velocity_signal.emit(self._velocity)
        return self._velocity  # на данном сканере нельзя получить скорость

    def acceleration(self) -> Acceleration:
        res = self._send_cmd('AAC')
        ans = Acceleration(*self._parse_A_res(res))
        self.acceleration_signal.emit(ans)
        return ans

    def deceleration(self) -> Deceleration:
        res = self._send_cmd('ADC')
        ans = Deceleration(*self._parse_A_res(res))
        self.deceleration_signal.emit(ans)
        return ans

    def _motor_on(self) -> BaseAxes:
        """
        Включены или выключены двигатели

        :return: покоординатные значения состояния двигателей
        """
        res = self._send_cmd('AMO')
        ans = BaseAxes(*self._parse_A_res(res, scale=False))
        return ans

    def _motion_mode(self) -> BaseAxes:
        """
        Режим движения двигателей

        :return: покоординатные значения режима движения двигателей
        """
        res = self._send_cmd('AMM')
        ans = BaseAxes(*self._parse_A_res(res, scale=False))
        return ans

    def _special_motion_mode(self) -> BaseAxes:
        """
        Специальный режим движения двигателей

        :return: покоординатные значения специального режима движения двигателей
        """
        res = self._send_cmd('ASM')
        ans = BaseAxes(*self._parse_A_res(res, scale=False))
        return ans

    def debug_info(self) -> str:
        cmds = [
            'AAP',  # следующая точка движения в PTP режиме
            'APS',  # актуальные координаты энкодеров
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

    @_motion_decorator
    def home(self) -> None:
        # уменьшение скорости в два раза
        old_velocity = self.velocity()
        new_velocity = old_velocity / 2
        self.set_settings(velocity=new_velocity)
        # выставляем режим бесконечного движения с постоянной скоростью
        self.set_settings(**JOG_MODE_SETTINGS)

        action_description = f'homing'
        cmds = ['XBG', 'YBG', 'ZBG']
        self._begin_motion_and_wait(cmds, action_description)

        # возвращаем старую скорость
        self.set_settings(velocity=old_velocity)
        # возвращаем point-to-point режим работы
        self.set_settings(**PTP_MODE_SETTINGS)

        stop_reasons = list(self._end_of_motion_reason())
        if not (stop_reasons[0] == stop_reasons[1] == stop_reasons[2] == 2):
            raise scanner_motion_error(action_description, stop_reasons)

    @property
    def position_signal(self) -> pyqtBoundSignal:
        return self._signals.position_signal

    @property
    def velocity_signal(self) -> pyqtBoundSignal:
        return self._signals.velocity_signal

    @property
    def acceleration_signal(self) -> pyqtBoundSignal:
        return self._signals.acceleration_signal

    @property
    def deceleration_signal(self) -> pyqtBoundSignal:
        return self._signals.deceleration_signal
