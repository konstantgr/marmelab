from TRIM import TRIMScanner, DEFAULT_SETTINGS
from tests.TRIM_emulator import run  # use it only for emulating
sc = TRIMScanner(ip="127.0.0.1", port=9000)

# TODO: Добавить подробную настройку движения сканнера:
#  скорость, ускорение, режим работы и тд, отображение сотояние мотора
def f_connection():
    """
    This function makes connection to the scanner
    """
    run(blocking=False, motion_time=10)  # use it only for emulating
    sc.connect()
    #sc.set_settings(**DEFAULT_SETTINGS) пока не работает
    print('Connected')


def f_up():
    """
    This function makes upward movement
    """
    from src import Position
    new_position = Position(x=0, y=10)
    sc.goto(new_position)
    print('moving up!')


def f_down():
    """
    This function makes downward movement
    """
    from src import Position
    new_position = Position(x=0, y=-10)
    sc.goto(new_position)
    print('moving down!')


def f_left():
    """
    This function makes movement to the left
    """
    from src import Position
    new_position = Position(x=-10, y=0)
    sc.goto(new_position)
    print('moving left!')

# TODO: Добавить относительное движение
def f_right():
    """
    This function makes movement to the right
    """
    from src import Position
    new_position = Position(x=10, y=0)
    sc.goto(new_position)
    print('moving right!')


def f_currrent_position():
    """
    This function shows current position
    """
    current_position = sc.position()
    print('x: ', current_position.x)
    print('y: ', current_position.y)
    print('z: ', current_position.z)


def abort():
    pass