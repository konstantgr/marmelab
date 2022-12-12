from src.scanner.TRIM.TRIM_emulator import run  # use it only for emulating
from pyqt_app import scanner
import logging
logger = logging.getLogger()


def f_connection():
    """
    This function makes connection to the scanner
    """
    run(blocking=False, motion_time=2)  # use it only for emulating
    scanner.connect()
    logger.info('Scanner is connected')


def f_default():
    """
    Функция - заглушка
    """
    pass


def f_moving_along_x(x_coord=10):
    """
    This function makes movement to the X positive direction
    """
    from src.scanner import Position
    old_x = scanner.position().x
    new_x = old_x + x_coord
    new_pos = Position(x=new_x)
    scanner.goto(new_pos)
    logger.info(f'Moving along x-axes on {x_coord}')


def f_moving_along_y(y_coord=10):
    """
    This function makes movement to the X positive direction
    """
    from src.scanner import Position
    old_y = scanner.position().y
    new_y = old_y + y_coord
    new_pos = Position(y=new_y)
    scanner.goto(new_pos)
    logger.info(f'Moving along y-axes on {y_coord}')


def f_moving_along_z(z_coord=10):
    """
    This function makes movement to the X positive direction
    """
    from src.scanner import Position
    old_z = scanner.position().z
    new_z = old_z + z_coord
    new_pos = Position(z=new_z)
    scanner.goto(new_pos)
    logger.info(f'Moving along z-axes on {z_coord}')


def f_moving_along_w(w_coord=10):
    """
    This function makes movement to the X positive direction
    """
    from src.scanner import Position
    old_w = scanner.position().w
    new_w = old_w + w_coord
    new_pos = Position(w=new_w)
    scanner.goto(new_pos)
    logger.info(f'Moving along w-axes on {w_coord}')


def f_abort():
    """
    This functions breaks any movements
    """
    pass


def f_button_default():
    pass


def f_home():
    """
    This function sets "home" current cords.
    """
    from src.scanner import Position
    scanner.home()
    scanner.set_settings(position=Position(0, 0, 0, 0))
    logger.debug("Scanner at home. Scanner position is:")
    current_position = scanner.position()
    logger.debug('x: ', current_position.x)
    logger.debug('y: ', current_position.y)
    logger.debug('z: ', current_position.z)
