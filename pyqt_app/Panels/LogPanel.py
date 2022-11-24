import logging
from PyQt6.QtWidgets import QHBoxLayout
from .BasePanel import BasePanel
from .LogWidget import QTextEditLogger

logger = logging.getLogger()


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
        logger.addHandler(logging_handler)  # добавление в логгер всего то, что получит обработчик
