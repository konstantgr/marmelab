import time
from typing import Any

from ..Project import PAnalyzer, PWidget, PAnalyzerSignals, PAnalyzerStates, PMeasurand
from ..Project import PMeasurable
from PyQt6.QtWidgets import QWidget, QTextEdit, QPushButton, QVBoxLayout, QSizePolicy, QGroupBox
from ..icons import control_icon, settings_icon
from PyQt6.QtCore import Qt, QThreadPool
from PyQt6.QtCore import pyqtBoundSignal, pyqtSignal, QObject
from ..Variable import Unit, Setting
from ..Widgets import SettingsTableWidget, StateDepPushButton
from ...analyzator.rohde_schwarz import RohdeSchwarzAnalyzer
from pyqtgraph import PlotWidget, PlotItem, PlotDataItem
import numpy as np


class Control(QWidget):
    def __init__(
            self,
            analyzer: RohdeSchwarzAnalyzer,
            states: PAnalyzerStates
    ):
        super(Control, self).__init__()
        self.analyzer = analyzer
        vbox = QVBoxLayout(self)
        vbox.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(vbox)

        self._thread_pool = QThreadPool()

        group = QGroupBox(self)
        group_layout = QVBoxLayout(group)
        group_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        vbox.addWidget(group)

        self.connect_button = StateDepPushButton(
            state=~states.is_connected & ~states.is_in_use,
            text="Connect",
            parent=self
        )
        self.disconnect_button = StateDepPushButton(
            state=states.is_connected & ~states.is_in_use,
            text="Disconnect",
            parent=self
        )

        self.connect_button.clicked.connect(analyzer.connect)
        self.disconnect_button.clicked.connect(analyzer.disconnect)

        group_layout.addWidget(self.connect_button)
        group_layout.addWidget(self.disconnect_button)

        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)


class Settings(SettingsTableWidget):
    def __init__(
            self,
            signals: PAnalyzerSignals,
            states: PAnalyzerStates,
            settings: list[Setting],
            parent: QWidget = None
    ):
        super(Settings, self).__init__(
            settings=settings,
            parent=parent,
            apply_state=states.is_connected & ~states.is_in_use
        )
        self.signals = signals

    def apply(self):
        self.signals.set_settings.emit(self.table.to_dict())


class TestMeasurandSignals(QObject):
    measure_signal: pyqtBoundSignal = pyqtSignal()


class TestMeasurand(PMeasurand):
    def __init__(self):
        super(TestMeasurand, self).__init__(name='test')
        self._plot_widget = PlotWidget()
        self._widget = QTextEdit('test')
        self._plot_item = PlotDataItem()
        self.measure_signals = TestMeasurandSignals()
        self.measure_signals.measure_signal.connect(self.redraw)

    @property
    def widget(self) -> QWidget:
        return self._widget

    @property
    def plot_widget(self):
        return self._plot_widget

    def redraw(self):
        x = np.linspace(0, 10, 100)
        self._plot_item.setData(x, np.sin(x) + np.random.normal(0, 0.1, 100))

    def measure(self) -> Any:
        time.sleep(1)
        self.measure_signals.measure_signal.emit()

    def pre_measure(self) -> None:
        plot = self._plot_widget.getPlotItem()  # type: PlotItem
        plot.clearPlots()
        self._plot_item = PlotDataItem()
        plot.addItem(self._plot_item)


class SParamasWidget(QGroupBox):
    def __init__(self):
        super(SParamasWidget, self).__init__()
        self.setLayout(QVBoxLayout())

        self.s_params_widget = QWidget(self)


class SParams(PMeasurand):
    def __init__(self, instrument: RohdeSchwarzAnalyzer):
        super(SParams, self).__init__(name='S-parameters')
        self._plot_widget = PlotWidget()
        self.instrument = instrument
        self._widget = SParamasWidget()

    @property
    def widget(self) -> QWidget:
        return self._widget

    @property
    def plot_widget(self):
        return self._plot_widget

    def measure(self) -> Any:
        time.sleep(1)

    def pre_measure(self) -> None:
        pass


class RohdeSchwarzPAnalyzer(PAnalyzer):
    def __init__(self, signals: PAnalyzerSignals, instrument: RohdeSchwarzAnalyzer,):
        super(RohdeSchwarzPAnalyzer, self).__init__(signals=signals, instrument=instrument)

        self._control_widgets = [
            PWidget(
                'Control',
                Control(instrument, self.states),
                icon=control_icon,
            ),
            PWidget(
                'Settings',
                Settings(self.signals, self.states, self._get_settings()),
                icon=settings_icon,
            )
        ]

    @property
    def control_widgets(self) -> list[PWidget]:
        return self._control_widgets

    @staticmethod
    def _get_settings() -> list[Setting]:
        res = [
            Setting(
                name='freq_start',
                unit=Unit(Hz=1),
                description='Start frequency',
                type=float,
                default_value=1000000,
            ),
            Setting(
                name='freq_stop',
                unit=Unit(Hz=1),
                description='Start frequency',
                type=float,
                default_value=2000000,
            ),
            Setting(
                name='freq_num',
                unit=Unit(Hz=1),
                description='Number of frequency points',
                type=float,
                default_value=200,
            ),
            Setting(
                name='channel',
                unit=Unit(),
                description='Channel',
                type=int,
                default_value=1,
            )
        ]
        return res

    def get_measurands(self) -> list[PMeasurand]:
        return [
            SParams(instrument=self.instrument),
            TestMeasurand()
        ]
