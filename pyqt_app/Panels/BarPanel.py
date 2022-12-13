from PyQt6.QtWidgets import QStatusBar, QLabel
from PyQt6.QtCore import pyqtSignal, pyqtBoundSignal


class BarPanel(QStatusBar):
    bar_status_signal: pyqtBoundSignal = pyqtSignal(str)

    def __init__(self, *args, **kwargs):
        super(BarPanel, self).__init__(*args, **kwargs)
        self._sc_status = QLabel(parent=self)  # сообщение сомнительно
        self._an_status = QLabel(parent=self)  # сообщение сомнительно
        self.addPermanentWidget(self._sc_status)
        self.addPermanentWidget(self._an_status)
        self.bar_status_signal.connect(self.temp_msg)  # подключение к сигналу

    def emit(self, record):
        self.bar_status_signal.emit(record)

    def temp_msg(self, msg):
        self.showMessage(str(msg), 10000)

    def sc_status_msg(self, msg):
        a = "connected" if msg else "not connected"
        self._sc_status.setText(f"Scanner: {a}")

    def an_status_msg(self, msg):
        a = "connected" if msg else "not connected"
        self._an_status.setText(f"Analyzer: {a}")