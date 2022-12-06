from src.scanner import Position, BaseAxes
from src.scanner.TRIM import DEFAULT_SETTINGS, TRIMScanner
from src.scanner.TRIM.TRIM import cmds_from_axes
from src.scanner.TRIM.TRIM import AXES_SCALE
from random import randint
import dataclasses


def test_cmds_from_dict():
    x = 123
    y = 342
    res = cmds_from_axes(BaseAxes(x=x, y=y), 'CMD')
    assert res == [f'XCMD={int(x * AXES_SCALE.x)}', f'YCMD={int(y * AXES_SCALE.y)}']
    res = cmds_from_axes(BaseAxes(x=x, y=y), 'CMD', val=False)
    assert res == [f'XCMD', f'YCMD']

    res = cmds_from_axes(BaseAxes(x=x), 'CMD')
    assert res == [f'XCMD={int(x * AXES_SCALE.x)}']
    res = cmds_from_axes(BaseAxes(x=x), 'CMD', val=False)
    assert res == [f'XCMD']


def test_get(TRIM_Scanner_emulator: TRIMScanner):
    for axis in [
        TRIM_Scanner_emulator.position,
        # TRIM_Scanner_emulator.velocity,
        TRIM_Scanner_emulator.acceleration,
        TRIM_Scanner_emulator.deceleration
    ]:
        assert axis().x == 10 / AXES_SCALE.x
        assert axis().y == 20 / AXES_SCALE.y
        assert axis().z == 30 / AXES_SCALE.z
        assert axis().w == 40 / AXES_SCALE.w


def test_set_settings(TRIM_Scanner_emulator: TRIMScanner):
    # тест velocity, acceleration, deceleration
    for setting, value in {
        TRIM_Scanner_emulator.position: {
            'position': BaseAxes(*[randint(0, 10) for _ in range(len(dataclasses.fields(BaseAxes)))])
        },
        TRIM_Scanner_emulator.velocity: {
            'velocity': BaseAxes(*[randint(0, 10) for _ in range(len(dataclasses.fields(BaseAxes)))])
        },
        TRIM_Scanner_emulator.acceleration: {
            'acceleration': BaseAxes(*[randint(0, 10) for _ in range(len(dataclasses.fields(BaseAxes)))])
        },
        TRIM_Scanner_emulator.deceleration: {
            'deceleration': BaseAxes(*[randint(0, 10) for _ in range(len(dataclasses.fields(BaseAxes)))])
        }
    }.items():
        TRIM_Scanner_emulator.set_settings(**value)
        d = dataclasses.asdict(value.popitem()[1])
        s = dataclasses.asdict(setting())
        assert all([s[key] == d[key] for key in d.keys() if d[key] is not None])

    # тест motor_on, motion_mode, special_motion_mode
    def send_and_check(req, res):
        for cmd, attr in {
            'AMO': {'motor_on': req},
            'AMM': {'motion_mode': req},
            'ASM': {'special_motion_mode': req}
        }.items():
            TRIM_Scanner_emulator.set_settings(**attr)
            assert TRIM_Scanner_emulator._send_cmd(cmd) == res
    # тест BaseAxes
    req = BaseAxes(x=randint(0, 10), y=randint(0, 10), z=randint(0, 10), w=randint(0, 20))
    res = f'{req.x},{req.y},{req.z},{req.w}'
    send_and_check(req, res)

    # reqB = AxesGroup(B=randint(0, 1))
    # res = f'{reqB.B},{reqB.B},{req.A},{req.A}'
    # send_and_check(reqB, res)


def test_set_default_settings(TRIM_Scanner_emulator: TRIMScanner):
    TRIM_Scanner_emulator.set_settings(**DEFAULT_SETTINGS)
    assert TRIM_Scanner_emulator.acceleration() == DEFAULT_SETTINGS['acceleration']
    assert TRIM_Scanner_emulator.deceleration() == DEFAULT_SETTINGS['deceleration']
    assert TRIM_Scanner_emulator.velocity() == DEFAULT_SETTINGS['velocity']

    for s, getter in {
        'motor_on': TRIM_Scanner_emulator._motor_on,
        'motion_mode': TRIM_Scanner_emulator._motion_mode,
        'special_motion_mode': TRIM_Scanner_emulator._special_motion_mode
    }.items():
        val = getter()
        assert val == DEFAULT_SETTINGS[s]


def test_goto(TRIM_Scanner_emulator: TRIMScanner):
    new_pos = Position(*[randint(0, 100) for _ in range(len(dataclasses.fields(BaseAxes)))])
    TRIM_Scanner_emulator.goto(new_pos)
    sc_pos = TRIM_Scanner_emulator.position()
    for field in dataclasses.fields(new_pos):
        attr = field.name
        assert sc_pos.__getattribute__(attr) == new_pos.__getattribute__(attr)


def test_debug(TRIM_Scanner_emulator: TRIMScanner):
    TRIM_Scanner_emulator.debug_info()


def test_home(TRIM_Scanner_emulator: TRIMScanner):
    TRIM_Scanner_emulator.home()
