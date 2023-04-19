from ..Project import PScanner, PScannerSignals, PScannerTypes
from src.Variable import Setting, Unit
from ...scanner.TRIM import TRIMScanner, DEFAULT_SETTINGS
from ...scanner.scanner import Position
from ..Worker import Worker
from PyQt6.QtCore import QThreadPool
from typing import Union

import logging
logger = logging.getLogger()


class TRIMPScanner(PScanner):
    def __init__(self, name: str, instrument: TRIMScanner, signals: PScannerSignals):
        super(TRIMPScanner, self).__init__(name=name, instrument=instrument, signals=signals)
        self._settings = []
        self.thread_pool = QThreadPool()
        UNITS = {
            'acceleration': Unit(m=1, s=-2),
            'deceleration': Unit(m=1, s=-2),
            'velocity': Unit(m=1, s=-1),
        }
        TYPES = {
            'motion_mode': int,
            'special_motion_mode': int,
            'motor_on': int
        }
        for key, value in DEFAULT_SETTINGS.items():
            for axis_name, axis_value in value.__dict__.items():
                var_name = f"{key}_{axis_name}"
                self._settings.append(Setting(
                    name=var_name,
                    unit=unit if (unit := UNITS.get(key)) is not None else Unit(),
                    description='',
                    type=type_ if (type_ := TYPES.get(key)) is not None else float,
                    default_value=axis_value,
                ))

    def set_settings(self, **settings):
        self.instrument.set_settings(**settings)

    def get_settings(self) -> list[Setting]:
        return self._settings

    @property
    def dims_number(self) -> int:
        return 3

    @property
    def axes_number(self) -> int:
        return 4

    def _home(self):
        self.instrument.home()
        self.instrument.set_settings(position=Position(2262.92, 2137.09, 0, 0))
        logger.debug("Scanner at home. Scanner position is:")
        current_position = self.instrument.position()
        logger.debug(f'x: {current_position.x}')
        logger.debug(f'y: {current_position.y}')
        logger.debug(f'z: {current_position.z}')
        logger.debug(f'w: {current_position.z}')

    def custom_home(self):
        worker = Worker(self._home)
        self.thread_pool.start(worker)

    def custom_goto(
            self,
            x: Union[float, int, None] = None,
            y: Union[float, int, None] = None,
            z: Union[float, int, None] = None,
            w: Union[float, int, None] = None):
        """Направить сканер в ручном режиме"""
        if \
                not (isinstance(x, (float, int)) or x is None) or\
                not (isinstance(y, (float, int)) or y is None) or\
                not (isinstance(z, (float, int)) or z is None) or\
                not (isinstance(w, (float, int)) or w is None):
            raise TypeError("float expected")
        position = Position(x=x, y=y, z=z, w=w)

        worker = Worker(self.instrument.goto, position)
        self.thread_pool.start(worker)
