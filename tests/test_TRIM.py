import pytest
from src import Velocity, Acceleration, Deceleration, Position, BaseAxes
from TRIM import AxesGroup, DEFAULT_SETTINGS, TRIMScanner
from random import randint


def test_axes_to_dict():
    A = randint(0, 100)
    B = randint(0, 100)
    el = AxesGroup(A=A, B=B)
    dct = el.to_dict()
    assert dct['A'] == A
    assert dct['B'] == B


def test_get(TRIM_Scanner_emulator: TRIMScanner):
    for axis in [
        TRIM_Scanner_emulator.position,
        TRIM_Scanner_emulator.velocity,
        TRIM_Scanner_emulator.acceleration,
        TRIM_Scanner_emulator.deceleration
    ]:
        assert axis().x == 10
        assert axis().y == 20
        assert axis().z == 30
        assert axis().w == 40


def test_set_settings(TRIM_Scanner_emulator: TRIMScanner):
    for setting, value in {
        TRIM_Scanner_emulator.velocity: {
            'velocity': BaseAxes(x=randint(0, 10), y=randint(0, 10), z=randint(0, 10))
        },
        TRIM_Scanner_emulator.acceleration: {
            'acceleration': BaseAxes(x=randint(0, 10), y=randint(0, 10), z=432)
        },
        TRIM_Scanner_emulator.deceleration: {
            'deceleration': BaseAxes(x=randint(0, 10), y=randint(0, 10), z=randint(0, 10))
        }
    }.items():

        TRIM_Scanner_emulator.set_settings(**value)
        d = value.popitem()[1].to_dict()
        s = setting().to_dict()
        assert all([s[key] == d[key] for key in d.keys() if d[key] is not None])

    t = BaseAxes(x=randint(0, 10), y=randint(0, 10), z=randint(0, 10), w=randint(0, 20))
    r = f'{t.x},{t.y},{t.z},{t.w}'

    TRIM_Scanner_emulator.set_settings(motor_on=t)
    assert TRIM_Scanner_emulator._send_cmd('AMO') == r
    TRIM_Scanner_emulator.set_settings(motion_mode=t)
    assert TRIM_Scanner_emulator._send_cmd('AMM') == r
    TRIM_Scanner_emulator.set_settings(special_motion_mode=t)
    assert TRIM_Scanner_emulator._send_cmd('ASM') == r


def test_goto(TRIM_Scanner_emulator: TRIMScanner):
    new_pos = Position(x=203)
    TRIM_Scanner_emulator.goto(new_pos)
    assert TRIM_Scanner_emulator.position().x == 203

