from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QSizePolicy, QSplitter, QTextEdit

from .BasePanel import BasePanel
from src.project import PScannerVisualizer, PAnalyzerVisualizer


class RightPanel(BasePanel):
    """
    This class makes widgets on the right panel
    """
    def __init__(
            self,
            scanner_visualizer: PScannerVisualizer,
            analyzer_visualizer: PAnalyzerVisualizer,
            **kwargs
    ):
        super(RightPanel, self).__init__(**kwargs)

        self.vbox = QVBoxLayout(self)
        self.setLayout(self.vbox)

        self.scanner_widget = scanner_visualizer.widget
        self.graph_widget = analyzer_visualizer.widget

        self.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Preferred)

        graphs_splitter = QSplitter(orientation=Qt.Orientation.Vertical)
        graphs_splitter.insertWidget(0, self.scanner_widget)
        graphs_splitter.insertWidget(1, self.graph_widget)
        self.vbox.addWidget(graphs_splitter)
