from MainWindow import *
from src import scanner_utils
import logging
logger = logging.getLogger()


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)
    logger.error(exception)

if __name__ == "__main__":
    sc = None
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setGeometry(300, 300, 900, 600)
    window.show()
    sys.excepthook = except_hook
    app.exec()

