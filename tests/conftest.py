import pytest
import threading
from src.scanner.TRIM import TRIMScanner
from src.scanner.TRIM.TRIM_emulator import emulator

TEST_IP = "127.0.0.1"
TEST_PORT = 9002
MOTION_TIME = 1

@pytest.fixture(scope="module")
def TRIM_Scanner_emulator():
    server_thread = threading.Thread(target=emulator, args=(TEST_IP, TEST_PORT, MOTION_TIME,))
    server_thread.start()

    sc = TRIMScanner(ip=TEST_IP, port=TEST_PORT)
    sc.connect()

    return sc
