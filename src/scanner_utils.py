from tests.TRIM_emulator import run  # use it only for emulating
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


def f_X_positive(x_coord=10):
    """
    This function makes movement to the X positive direction
    """
    from src import Position
    old_x = scanner.position().x
    new_x = old_x + x_coord
    new_pos = Position(x=new_x)
    scanner.goto(new_pos)
    logger.info(f'Moving along x-axes on {x_coord}')


def f_go_table(x_coord=0, y_coord=0, z_coord=0, w_coord=0):
    """
    This function makes movement by coords from table
    """
    from src import Position
    old_x = scanner.position().x
    old_y = scanner.position().y
    old_z = scanner.position().z
    old_w = scanner.position().w

    new_x = old_x + x_coord  # не работает...
    new_y = old_y + y_coord
    new_z = old_z + z_coord
    new_w = old_z + w_coord
    new_pos = Position(x=new_x, y=new_y, z=new_z, w=new_w)
    scanner.goto(new_pos)

    logger.debug("Scanner position is:")
    logger.debug('x: ', new_pos.x)
    logger.debug('y: ', new_pos.y)
    logger.debug('z: ', new_pos.z)


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
    from src import Position
    scanner.home()
    scanner.set_settings(position=Position(0, 0, 0, 0))
    logger.debug("Scanner at home. Scanner position is:")
    current_position = scanner.position()
    logger.debug('x: ', current_position.x)
    logger.debug('y: ', current_position.y)
    logger.debug('z: ', current_position.z)