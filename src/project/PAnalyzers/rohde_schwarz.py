import dataclasses
import time
from typing import Any

from ..Project import PAnalyzer, PAnalyzerSignals, PAnalyzerStates, PMeasurand
from PyQt6.QtWidgets import QWidget, QTextEdit, QCheckBox, QComboBox, QPushButton, QGridLayout, QVBoxLayout, QSizePolicy, QGroupBox
from src.icons import control_icon
from PyQt6.QtCore import Qt, QThreadPool
from PyQt6.QtCore import pyqtBoundSignal, pyqtSignal, QObject
from PyQt6.QtGui import QColor
from src.Variable import Unit, Setting
from src.views.Widgets import SettingsTableWidget, StateDepPushButton
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


@dataclasses.dataclass
class SParam:
    """Класс S-параметра, который хранит его настройки"""
    enable: bool = False
    name: str = 'S11'
    units: str = 'dBMag'
    color: QColor = None


class SParamsModel:
    def __init__(
            self,
            analyzer: RohdeSchwarzAnalyzer,
            s_size: int = 2,
    ):
        self.analyzer = analyzer
        self.s_size = s_size
        self.freq_start = 1*1e9
        self.freq_stop = 5*1e9
        self.freq_num = 50
        self.s_params = []
        for i in range(s_size):
            for j in range(s_size):
                self.s_params.append(SParam(
                    enable=(i == j == 0),
                    name=f'S{i+1}{j+1}',
                    color=QColor('blue'),
                ))

    def pre_measure(self):
        self.analyzer.set_settings(
            freq_start=self.freq_start,
            freq_stop=self.freq_stop,
            freq_num=self.freq_num
        )

    def measure(self) -> dict[str: Any]:
        req = []
        for s_param in self.s_params:
            if s_param.enable:
                req.append(s_param.name)
        return self.analyzer.get_scattering_parameters(req)

    # def get_s_param(self, index: int) -> SParam:
    #     return self.s_params[index]

    def set_s_param(
            self,
            index: int,
            enable: bool = None,
            name: str = None,
            units: str = None,
            color: QColor = None,
    ):
        if enable is not None:
            self.s_params[index].enable = enable
        if name is not None:
            self.s_params[index].name = name
        if units is not None:
            self.s_params[index].units = units
        if color is not None:
            self.s_params[index].color = color

    def set_freq(
            self,
            freq_start: float = None,
            freq_stop: float = None,
            freq_num: int = None,
    ):
        if freq_start is not None:
            self.freq_start = freq_start
        if freq_stop is not None:
            self.freq_stop = freq_stop
        if freq_num is not None:
            self.freq_num = freq_num


class SParamsFreq(SettingsTableWidget):
    def __init__(
            self,
            settings: list[Setting],
            model: SParamsModel,
    ):
        super(SParamsFreq, self).__init__(settings=settings, default_settings_button=False)
        self.model = model

    def apply(self):
        r = self.table.to_dict()
        self.model.set_freq(r['freq_start'], r['freq_stop'], r['freq_num'])
        self.model.pre_measure()


class SParamasWidget(QGroupBox):
    def __init__(
            self,
            model: SParamsModel,
    ):
        super(SParamasWidget, self).__init__()
        self.model = model

        self.setLayout(QVBoxLayout())
        self.s_params_widget = QWidget(self)
        self.layout().addWidget(self.s_params_widget)

        layout = QGridLayout()
        self.s_params_widget.setLayout(layout)
        for i, s_param in enumerate(self.model.s_params):
            enable = QCheckBox()
            enable.setChecked(s_param.enable)
            layout.addWidget(enable, i, 0)

            param = QComboBox()
            for k in range(model.s_size):
                for j in range(model.s_size):
                    param.addItem(f'S{k+1}{j+1}')
            layout.addWidget(param, i, 1)

            unit = QComboBox()
            unit.addItem('dBMag')
            layout.addWidget(unit, i, 2)

            color = QPushButton('Color')
            color.setStyleSheet(f"background-color: rgb{s_param.color.getRgb()[0:-1]}")
            layout.addWidget(color, i, 3)

        self.freq_widget = SParamsFreq(
            settings=[
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
            ],
            model=self.model
        )

        self.layout().addWidget(self.freq_widget)


class SParams(PMeasurand):
    def __init__(self, analyzer: RohdeSchwarzAnalyzer):
        super(SParams, self).__init__(name='S-parameters')
        self._plot_widget = PlotWidget()
        self._plot_item = PlotDataItem()
        self.analyzer = analyzer
        self._model = SParamsModel(analyzer=self.analyzer)
        self._widget = SParamasWidget(model=self._model)

    @property
    def widget(self) -> QWidget:
        return self._widget

    @property
    def plot_widget(self):
        return self._plot_widget

    def measure(self) -> Any:
        res = self._model.measure()
        self._plot_item.setData(res['f'], np.abs(res['S11']))
        return res

    def pre_measure(self) -> None:
        plot = self._plot_widget.getPlotItem()  # type: PlotItem
        plot.clearPlots()
        self._plot_item = PlotDataItem()
        plot.addItem(self._plot_item)
        self._model.pre_measure()


class RohdeSchwarzPAnalyzer(PAnalyzer):
    def __init__(self, signals: PAnalyzerSignals, instrument: RohdeSchwarzAnalyzer,):
        super(RohdeSchwarzPAnalyzer, self).__init__(
            signals=signals,
            instrument=instrument
        )

        self._control_widgets = [
            PWidget(
                'Control',
                Control(instrument, self.states),
                icon=control_icon,
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
            SParams(analyzer=self.instrument),
            TestMeasurand()
        ]
