

def f_connection():
    """
    This function makes connection to the scanner
    """

    from tests.TRIM_emulator import run  # use it only for emulating
    run(blocking=False)  # use it only for emulating
    from TRIM import TRIMScanner
    global sc
    sc = TRIMScanner(ip="127.0.0.1", port=9000)
    sc.connect()
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
    print('moving down!')


def f_left():
    """
    This function makes movement to the left
    """
    print('moving left!')


def f_right():
    """
    This function makes movement to the right
    """
    print('moving right!')


def f_currrent_position():
    """
    This function shows current position
    """
    current_position = sc.position()
    print('x: ', current_position.x)
    print('y: ', current_position.y)
    print('z: ', current_position.z)
