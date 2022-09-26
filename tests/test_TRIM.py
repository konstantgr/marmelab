import pytest
import socket
from TRIM import TRIMScanner, Axes, AxesSettings, DEFAULT_SETTINGS
import random

def TRIM_emulator():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 9001))
        s.listen()
        conn, addr = s.accept()
        with conn:
            while True:
                data = conn.recv(1024)
                if not data:
                    break
                conn.sendall(data)


def test_axes_to_dict():
    x = random.randint(0, 100)
    A = random.randint(0, 100)
    B = random.randint(0, 100)
    el = Axes(A=A, B=B, x=x)
    dct = el.to_dict()
    assert dct['x'] == x
    assert dct['y'] is None
    assert dct['z'] is None
    assert dct['w'] is None
    assert dct['A'] == A
    assert dct['B'] == B
