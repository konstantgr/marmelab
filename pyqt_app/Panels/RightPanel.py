from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QVBoxLayout, QSizePolicy, QSplitter

from pyqt_app import scanner
from . import RightWidgets
from .BasePanel import BasePanel


class RightPanel(BasePanel):
    """
    This class makes widgets on the right panel
    """
    def __init__(self, *args, **kwargs):
        super(RightPanel, self).__init__(*args, **kwargs)

        self.vbox = QVBoxLayout(self)
        self.setLayout(self.vbox)

        self.scanner_widget = RightWidgets.ScannerVisualizer(self)
        self.graph_widget = RightWidgets.GraphWidget(self)

        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Preferred)

        graphs_splitter = QSplitter(orientation=Qt.Orientation.Vertical)
        graphs_splitter.insertWidget(0, self.scanner_widget)
        graphs_splitter.insertWidget(1, self.graph_widget)
        self.vbox.addWidget(graphs_splitter)

        scanner.position_signal.connect(self.scanner_widget.set_scanner_pos)