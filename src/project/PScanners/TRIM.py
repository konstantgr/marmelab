from ..Project import PScanner, PScannerSignals, PScannerTypes
from src.Variable import Setting, Unit
from ...scanner.TRIM import TRIMScanner, DEFAULT_SETTINGS

import logging
logger = logging.getLogger()


class TRIMPScanner(PScanner):
    def __init__(self, name: str, instrument: TRIMScanner, signals: PScannerSignals):
        super(TRIMPScanner, self).__init__(name=name, instrument=instrument, signals=signals)
        self._settings = []
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




