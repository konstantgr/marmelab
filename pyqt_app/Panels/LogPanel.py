import logging

from PyQt6.QtCore import QObject, pyqtBoundSignal, pyqtSignal
from PyQt6.QtWidgets import QHBoxLayout, QPlainTextEdit
from .BasePanel import BasePanel

logger = logging.getLogger()


class QTextEditLogger(logging.Handler, QObject):
    appendPlainText: pyqtBoundSignal = pyqtSignal(str)  # инициализация сигнала вместо дефолтного

    def __init__(self, parent):
        super().__init__()
        QObject.__init__(self)
        self.widget = QPlainTextEdit(parent)  # создание виджета пустого окна
        self.widget.setReadOnly(True)
        self.appendPlainText.connect(self.widget.appendPlainText)  # вызов функции, которая добавляет текст

    def emit(self, record):
        msg = self.format(record)
        self.appendPlainText.emit(msg)  # добавление в сигнал строки, которая передается в исполняемую функцию


class LogPanel(BasePanel):
    """
    This class makes widgets on the log panel
    """
    def __init__(self, *args, **kwargs):
        super(LogPanel, self).__init__(*args, **kwargs)
        hbox = QHBoxLayout(self)
        logging_handler = QTextEditLogger(self)
        logging_handler.setFormatter(
            logging.Formatter(
                '%(asctime)s %(levelname)s: %(message)s')
        )

        hbox.addWidget(logging_handler.widget)
        self.setLayout(hbox)
        logger.addHandler(logging_handler)  # добавление в логгер всего того, что получит обработчик
