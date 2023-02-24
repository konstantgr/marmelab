from .Widgets import SettingsTableWidget
from ..project.PVisualizers.ScannerVisualizer import ScannerVisualizer, DEFAULT_SETTINGS
from .View import BaseView, QWidgetType
from PyQt6.QtWidgets import QWidget, QSplitter, QVBoxLayout
from PyQt6.QtCore import Qt

import logging
logger = logging.getLogger()


class ScannerVisualizer3DSettings(BaseView):
    def __init__(self, *args, **kwargs):
        super(ScannerVisualizer3DSettings, self).__init__(*args, **kwargs)
        self.visualizer: ScannerVisualizer = self.model
        self.settings_table = SettingsTableWidget(
            settings=DEFAULT_SETTINGS,
            apply=self.apply
        )

    def construct_widget(self) -> QWidgetType:
        widget = QWidget()
        widget.setLayout(QVBoxLayout())
        splitter = QSplitter(orientation=Qt.Orientation.Vertical)
        widget.layout().addWidget(splitter)
        widget.layout().setContentsMargins(0, 0, 0, 0)

        splitter.addWidget(self.settings_table)
        splitter.addWidget(QWidget())
        splitter.setChildrenCollapsible(False)
        splitter.setProperty('type', 'inner')
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 1)
        return widget

    def apply(self):
        self.visualizer.set_settings(**self.settings_table.table.to_dict())
