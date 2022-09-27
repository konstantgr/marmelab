import pytest
import threading
from TRIM import TRIMScanner
from TRIM_emulator import emulator

TEST_IP = "127.0.0.1"
TEST_PORT = 9002


@pytest.fixture(scope="module")
def TRIM_Scanner_emulator():
    server_thread = threading.Thread(target=emulator, args=(TEST_IP, TEST_PORT,))
    server_thread.start()

    sc = TRIMScanner(ip=TEST_IP, port=TEST_PORT)
    sc.connect()

    return sc