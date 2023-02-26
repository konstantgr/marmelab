from ..Project import PScannerVisualizer, PStorage, PScanner, ProjectType, PBaseTypes
from typing import List
from PyQt6.QtWidgets import QWidget
from src.Variable import Setting, Unit
from typing import Dict
from numbers import Number
from PyQt6.QtCore import pyqtBoundSignal, pyqtSignal, QObject


DEFAULT_SETTINGS = [
    Setting(
        name='room_size_x',
        unit=Unit(m=1),
        description='',
        default_value=3000,
    ),
    Setting(
        name='room_size_y',
        unit=Unit(m=1),
        description='',
        default_value=3000,
    ),
    Setting(
        name='room_size_z',
        unit=Unit(m=1),
        description='',
        default_value=5000,
    ),
    Setting(
        name='scanner_zone_size_x',
        unit=Unit(m=1),
        description='',
        default_value=2262.92,
    ),
    Setting(
        name='scanner_zone_size_y',
        unit=Unit(m=1),
        description='',
        default_value=2137.09,
    ),
    Setting(
        name='scanner_zone_size_z',
        unit=Unit(m=1),
        description='',
        default_value=531.4,
    ),
    Setting(
        name='scanner_offset_x',
        unit=Unit(m=1),
        description='',
        default_value=368.54,
    ),
    Setting(
        name='scanner_offset_y',
        unit=Unit(m=1),
        description='',
        default_value=300,
    ),
    Setting(
        name='scanner_offset_z',
        unit=Unit(m=1),
        description='',
        default_value=200,
    ),
    Setting(
        name='scanner_L_x',
        unit=Unit(m=1),
        description='',
        default_value=0,
    ),
    Setting(
        name='scanner_L_y',
        unit=Unit(m=1),
        description='',
        default_value=0,
    ),
    Setting(
        name='scanner_L_z',
        unit=Unit(m=1),
        description='',
        default_value=200,
    ),

]


class xyzwScannerVisualizerSignals(QObject):
    settings_updated: pyqtBoundSignal = pyqtSignal()


class xyzwScannerVisualizer(PScannerVisualizer):
    def __init__(
            self, name: str, scanner: PScanner, objects: PStorage, paths: PStorage,
    ):
        super(xyzwScannerVisualizer, self).__init__(name=name)
        self.scanner = scanner
        self.signals = xyzwScannerVisualizerSignals()
        self.objects = objects
        self.paths = paths
        self.settings = {setting.name: setting.default_value for setting in DEFAULT_SETTINGS}

    def get_default_settings(self) -> List[Setting]:
        return DEFAULT_SETTINGS

    def set_settings(self, settings: Dict[str, Number]):
        self.settings = settings
        self.signals.settings_updated.emit()

    def get_settings(self) -> Dict[str, Number]:
        return self.settings



