from src import BaseAxes, Position, Velocity, Deceleration, Acceleration
import random


def test_axes_to_dict():
    for cl in [BaseAxes, Position, Velocity, Deceleration, Acceleration]:
        x = random.randint(0, 100)
        y = random.randint(0, 100)
        z = random.randint(0, 100)
        w = random.randint(0, 100)
        el = cl(x=x, y=y, z=z, w=w)
        dct = el.to_dict()
        assert dct['x'] == x
        assert dct['y'] == y
        assert dct['z'] == z
        assert dct['w'] == w

