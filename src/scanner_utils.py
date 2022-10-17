from TRIM import TRIMScanner, DEFAULT_SETTINGS
from tests.TRIM_emulator import run  # use it only for emulating
sc = TRIMScanner(ip="127.0.0.1", port=9000)

# TODO: Добавить подробную настройку движения сканнера:
#  скорость, ускорение, режим работы и тд, отображение сотояние мотора
#  для этого есть функция set_settings()
def f_connection():
    """
    This function makes connection to the scanner
    """
    run(blocking=False, motion_time=10)  # use it only for emulating
    sc.connect()
    #sc.set_settings(**DEFAULT_SETTINGS) пока не работает
    print('Connected')


def f_up_edit():
    """
    This function makes upward movement
    """
    from src import Position
    new_position = Position()
    sc.goto(new_position)
    print('moving up!')


def f_up():
    """
    This function makes upward movement
    """

    from src import Position
    # old_pos = sc.position()
    # new_pos = old_pos + Position(x=10)         !!! Doesn`t work !!!
    # sc.goto(new_pos)

    old_x = sc.position().x
    new_x = old_x + 10
    new_pos = Position(x=new_x)
    sc.goto(new_pos)

    print('moving up!')


def f_down():
    """
    This function makes downward movement
    """
    from src import Position
    new_position = Position(x=0, y=-10)
    sc.goto(new_position)
    print('moving down!')


# TODO: Добавить функции управления сканнером в положительном и отрицительном направлениях
# TODO: Добавить управление через значения, задаваемые в окошках



# TODO: не работает передача значений фукции
def f_X_positive(x_coord):
    """
    This function makes movement to the left
    """
    from src import Position
    old_x = sc.position().x
    new_x = old_x + x_coord
    new_pos = Position(x=new_x)
    sc.goto(new_pos)

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

def f_default():
    """
    Функция - заглушка
    """

    pass



def abort():
    pass