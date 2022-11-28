from TRIM import TRIMScanner
import logging
from logging.handlers import RotatingFileHandler
import os
from pathlib import Path
from src.analyzator.rohde_schwarz.rohde_schwarz import RohdeSchwarzAnalyzator
import yaml

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# in-file logging

logs_folder_path = os.path.join(Path(__file__).parents[1], 'logs')
if not os.path.exists(logs_folder_path):
    os.mkdir(logs_folder_path)
logs_path = os.path.join(logs_folder_path, 'logs.txt')

fh = RotatingFileHandler(logs_path, maxBytes=1048576, backupCount=10, encoding='utf-8')
fh.setFormatter(logging.Formatter('%(asctime)s [%(levelname)s]: %(message)s'))
logger.addHandler(fh)

with open(os.path.join(os.path.dirname(__file__), 'config.yml'), 'r') as file:
    config = yaml.safe_load(file)
    scanner_settings = config['scanner']
    analyzer_settings = config['analyzer']

scanner = TRIMScanner(ip=scanner_settings['ip'], port=int(scanner_settings['port']))
analyzator = RohdeSchwarzAnalyzator(ip=analyzer_settings['ip'], port=analyzer_settings['port'])
