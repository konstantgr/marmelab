from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QSizePolicy, QSplitter, QTextEdit
from PyQt6.QtGui import QGuiApplication
from .BasePanel import BasePanel
from src.project import PScannerVisualizer, PAnalyzerVisualizer
from src.ModelView import ModelViewVisualizer


class RightPanel(BasePanel):
    """
    This class makes widgets on the right panel
    """
    def __init__(
            self,
            scanner_visualizer: ModelViewVisualizer,
            plots_visualizer: ModelViewVisualizer,
            **kwargs
    ):
        super(RightPanel, self).__init__(**kwargs)

        self.vbox = QVBoxLayout(self)
        self.setLayout(self.vbox)
        self.scanner_widget = scanner_visualizer.visualizer_widget.widget
        self.plots_widget = plots_visualizer.visualizer_widget.widget

        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        graphs_splitter = QSplitter(orientation=Qt.Orientation.Vertical)
        graphs_splitter.insertWidget(0, self.scanner_widget)
        graphs_splitter.insertWidget(1, self.plots_widget)
        max_height = QGuiApplication.primaryScreen().virtualSize().height()
        graphs_splitter.setSizes([int(max_height/3), int(max_height/2)])
        self.vbox.addWidget(graphs_splitter)
