from ..Project import PScanner, PScannerSignals
from ...Variable import Setting, Unit
from ...scanner.TRIM import TRIMScanner


class ToyScanner(PScanner):
    def __init__(
            self,
            instrument: TRIMScanner,
            signals: PScannerSignals
    ):
        super(ToyScanner, self).__init__(instrument=instrument, signals=signals)
        self._Settings = [
            Setting(
                name="Velocity",
                unit=Unit(m=1, s=-1),
                description="Скорость",
                default_value=100
            )
        ]

    def get_settings(self) -> list[Setting]:
        return self._Settings
