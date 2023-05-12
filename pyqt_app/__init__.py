import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
from PyQt6.QtWidgets import QApplication
import sys

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# in-file logging
logs_folder_path = os.path.join(Path(__file__).parents[1], 'logs')
if not os.path.exists(logs_folder_path):
    os.mkdir(logs_folder_path)
logs_path = os.path.join(logs_folder_path, 'logs.txt')

fh = RotatingFileHandler(logs_path, maxBytes=1048576, backupCount=10, encoding='utf-8')
fh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s] %(name)s: %(message)s'))
logger.addHandler(fh)

gl_logger = logging.getLogger('OpenGL.GL.shaders')
gl_logger.setLevel(logging.ERROR)


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)
    logger.error(exception, exc_info=(cls, exception, traceback))


sys.excepthook = except_hook
app = QApplication(sys.argv)

from .app_project import project, builder


