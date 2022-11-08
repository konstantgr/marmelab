from TRIM import TRIMScanner
import logging

logger = logging.getLogger()
logger.setLevel(logging.INFO)

scanner = TRIMScanner(ip="127.0.0.1", port=9000)
