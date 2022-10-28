import threading
import time

import TRIM
import src
from tests import TRIM_emulator
from TRIM import TRIMScanner
from src import Position

# TRIM_emulator.run(blocking=False, ip='127.0.0.1', port=9000, motion_time=5)
# scanner = TRIMScanner(ip='127.0.0.1', port=9000)
scanner = TRIMScanner(ip='192.168.5.168', port=9000)
scanner.connect()

scanner.set_settings(**TRIM.DEFAULT_SETTINGS)


def debug():
    print(scanner.debug_info())


def print_pos(go):
    while go[0]:
        print(scanner.position())
        time.sleep(1)


def goto(x):
    go = [True]
    th = threading.Thread(target=print_pos, args=(go,))
    old_pos = scanner.position()
    new_pos = old_pos + Position(x=x)
    th.start()
    scanner.goto(new_pos)
    go[0] = False
    th.join()


def stop_after_n_sec(n):
    time.sleep(n)
    scanner.stop()


def abort_after_n_sec(n):
    time.sleep(n)
    scanner.abort()


def MO_after_n_sec(n):
    time.sleep(n)
    scanner._send_cmd('XMO=0')


def XST_after_n_sec(n):
    time.sleep(n)
    scanner._send_cmd('XST')


def goto_and_func(x, func):
    go = [True]
    th = threading.Thread(target=print_pos, args=(go,))
    th2 = threading.Thread(target=func, args=(2,))
    old_pos = scanner.position()
    new_pos = old_pos + Position(x=x)
    th.start()
    th2.start()
    try:
        scanner.goto(new_pos)
    except src.ScannerMotionError as e:
        print(e)
    time.sleep(2)
    go[0] = False
    th.join()
    th2.join()


def homing():
    go = [True]
    th = threading.Thread(target=print_pos, args=(go,))
    th.start()
    scanner.home()
    go[0] = False
    th.join()


def stop1(x):
    go = [True]
    th = threading.Thread(target=print_pos, args=(go,))
    old_pos = scanner.position()
    new_pos = old_pos + Position(x=x)

    th1 = threading.Thread(target=scanner.goto, args=(new_pos,))
    th2 = threading.Thread(target=scanner.goto, args=(old_pos,))

    error_thread = threading.Thread(target=stop_after_n_sec, args=(2,))

    th.start()
    th1.start()
    th2.start()
    error_thread.start()
    th1.join()
    th2.join()
    error_thread.join()
    go[0] = False
    th.join()


debug()
time.sleep(5)
# scanner.set_settings()
goto(-int(500*2**13))
# scanner.set_settings(position=Position(x=0, y=0, z=0))
# goto_and_func(x=-2000000, func=stop_after_n_sec)
# goto_and_func(x=-2000000, func=abort_after_n_sec)
# goto_and_func(x=2000000, func=MO_after_n_sec)
# goto_and_func(x=2000000, func=XST_after_n_sec)
# time.sleep(4)
# homing()
# stop1(-2000000)

# scanner.stop()
debug()


scanner.disconnect()

# переделать stop_reason: если не стартовал, то не надо проверять
# velocity не работает (кек)
