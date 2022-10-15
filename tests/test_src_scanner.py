from src import BaseAxes, Position, Velocity, Deceleration, Acceleration
from random import randint
import dataclasses
import pytest


def test_axes_to_dict():
    for cl in [BaseAxes, Position, Velocity, Deceleration, Acceleration]:
        el = cl(*[randint(0, 10) for _ in range(len(dataclasses.fields(cl)))])
        dct = el.to_dict()
        for field in dataclasses.fields(cl):
            name = field.name
            assert dct[name] == el.__getattribute__(name)


def test_axes_add_sub():
    for cl in [BaseAxes, Position, Velocity, Deceleration, Acceleration]:
        el1 = cl(*[randint(0, 10) for _ in range(len(dataclasses.fields(cl)))])
        el2 = cl(*[randint(0, 10) for _ in range(len(dataclasses.fields(cl)))])

        el3 = el1 + el2
        assert isinstance(el3, BaseAxes)
        for field in dataclasses.fields(cl):
            name = field.name
            assert el3.__getattribute__(name) == el1.__getattribute__(name) + el2.__getattribute__(name)

        el3 = el1 - el2
        assert isinstance(el3, BaseAxes)
        for field in dataclasses.fields(cl):
            name = field.name
            assert el3.__getattribute__(name) == el1.__getattribute__(name) - el2.__getattribute__(name)

        el1 = cl(x=1)
        el2 = cl(x=None)
        el3 = el1 + el2
        assert el3.x == 1
        with pytest.raises(TypeError):
            el3 = el2 + el1
