from ..Project import PMeasurable, PMeasurand, PAnalyzer
from PyQt6.QtWidgets import QWidget, QComboBox
from pyqtgraph import PlotWidget
from typing import Any
from PyQt6.QtWidgets import QVBoxLayout, QStackedWidget
from PyQt6.QtCore import pyqtBoundSignal, pyqtSignal, QObject


class ModelSignals(QObject):
    """Сигналы"""
    current_measurand_index: pyqtBoundSignal = pyqtSignal(int)


class Model:
    """Модель"""
    def __init__(
            self,
            analyzer: PAnalyzer,

    ):
        self.analyzer = analyzer
        self.measurands = self.analyzer.get_measurands()
        self.current_measurand_index = 0
        self.signals = ModelSignals()

        self._update_current_measurand()

    def set_current_measurand_index(self, index: int):
        """
        Установить текущий measurand

        :param index: индекс в списке measurands
        """
        if index != self.current_measurand_index:
            self.current_measurand_index = index
            self._update_current_measurand()

    def _update_current_measurand(self):
        index = self.current_measurand_index
        self.current_measurand = self.measurands[index]
        self.signals.current_measurand_index.emit(index)

    def get_measurand(self, index: int) -> PMeasurand:
        """
        measurand

        :param index: индекс в списке measurands
        """
        return self.measurands[index]

    def get_measurands_len(self) -> int:
        """Количество measurand"""
        return len(self.measurands)

    def measure(self) -> Any:
        """
        Провести измерение
        """
        # проверка, выставлены ли необходимые настройки на сканере
        if self.analyzer.current_measurand is not self.current_measurand:
            self.current_measurand.pre_measure()
            self.analyzer.set_current_measurand(self.current_measurand)
        return self.current_measurand.measure()


class MeasurableWidget(QWidget):
    """
    Вьюшка
    """
    def __init__(
            self,
            model: Model,

    ):
        super(MeasurableWidget, self).__init__()
        self.model = model

        self.setLayout(QVBoxLayout())
        self.combo_box = QComboBox()
        self.stacked_widgets = QStackedWidget()
        self.layout().addWidget(self.combo_box)
        self.layout().addWidget(self.stacked_widgets)

        self.combo_box.currentIndexChanged.connect(self.model.set_current_measurand_index)
        self.model.signals.current_measurand_index.connect(self.set_current_measurand)
        self.update_measurands()

    def set_current_measurand(self, i):
        """Выбор нужного виджета в QStackedWidget"""
        self.stacked_widgets.setCurrentIndex(i)

    def update_measurands(self):
        """Перерисовка всех виджетов"""
        self.combo_box.clear()
        for i in range(self.stacked_widgets.count()):
            self.stacked_widgets.removeWidget(self.stacked_widgets.widget(i))

        for index in range(self.model.get_measurands_len()):
            measurand = self.model.get_measurand(index)
            self.combo_box.addItem(measurand.name)
            self.stacked_widgets.addWidget(measurand.widget)


class MeasurableOfMeasurands(PMeasurable):
    def __init__(
            self,
            name: str,
            analyzer: PAnalyzer,
    ):
        model = Model(
            analyzer=analyzer,
        )
        widget = MeasurableWidget(
            model=model,
        )
        super(MeasurableOfMeasurands, self).__init__(
            name=name,
            widget=widget,
        )
        self._model = model
        self._model.signals.current_measurand_index.connect(self._changed)

    def _changed(self, *args, **kwargs):
        # оповещаем всех, что PMeasurable изменился
        self.signals.changed.emit()

    @property
    def plot_widget(self) -> PlotWidget:
        return self._model.current_measurand.plot_widget

    def measure(self) -> Any:
        return self._model.measure()
