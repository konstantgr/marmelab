from TRIM import TRIMScanner
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
from analyzator.rohde_schwarz.rohde_schwarz import RohdeSchwarzAnalyzator

logger = logging.getLogger()
logger.setLevel(logging.INFO)

scanner = TRIMScanner(ip="127.0.0.1", port=9000)
analyzator = RohdeSchwarzAnalyzator(ip="192.168.5.168", port="9000")
# in-file logging

logs_folder_path = os.path.join(Path(__file__).parents[1], 'logs')
if not os.path.exists(logs_folder_path):
    os.mkdir(logs_folder_path)
logs_path = os.path.join(logs_folder_path, 'logs.txt')

fh = RotatingFileHandler(logs_path, maxBytes=1048576, backupCount=10, encoding='utf-8')
fh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s'))
logger.addHandler(fh)
