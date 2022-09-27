import pytest
from src import Velocity, Acceleration, Deceleration
from TRIM import Axes, AxesSettings, DEFAULT_SETTINGS
import random


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


def test_axes_settings_to_cmd():
    velocity = Velocity(x=10)
    acceleration = Acceleration(z=320)
    deceleration = Deceleration(y=33)
    motor_on = Axes(B=0)
    motion_mode = Axes(A=0)
    special_motion_mode = Axes(A=1, B=0)
    s = AxesSettings(
        velocity=velocity,
        acceleration=acceleration,
        deceleration=deceleration,
        motor_on=motor_on,
        motion_mode=motion_mode,
        special_motion_mode=special_motion_mode
    )
    cmds = s.to_cmds()
    assert cmds.count('XSP=10') == 1
    assert cmds.count('ZAC=320') == 1
    assert cmds.count('YDC=33') == 1
    assert cmds.count('BMO=0') == 1
    assert cmds.count('AMM=0') == 1
    assert cmds.count('ASM=1') == 1
    assert cmds.count('BSM=0') == 1
