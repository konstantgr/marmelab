from TRIM import TRIMScanner, DEFAULT_SETTINGS
from tests.TRIM_emulator import run  # use it only for emulating
sc = TRIMScanner(ip="127.0.0.1", port=9000)
from tkinter import messagebox
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




# TODO: Добавить функции управления сканнером в положительном и отрицительном направлениях
# TODO: Добавить управление через значения, задаваемые в окошках


def f_currrent_position():
    """
    This function shows current position
    """
    current_position = sc.position()
    messagebox.showinfo("Scanner", f"x: {current_position.x}\ny: {current_position.y}\nz: {current_position.z}")




    print('x: ', current_position.x)
    print('y: ', current_position.y)
    print('z: ', current_position.z)

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
    old_x = sc.position().x
    new_x = old_x + x_coord
    new_pos = Position(x=new_x)
    sc.goto(new_pos)
    print(f'Moving along x-axes on {x_coord}')


def f_go_table(x_coord=0, y_coord=0, z_coord=0):
    """
    This function makes movement by coords from table
    """
    from src import Position
    old_x = sc.position().x
    old_y = sc.position().y
    old_z = sc.position().z

    new_x = old_x + x_coord  # не работает...
    new_y = old_y + y_coord
    new_z = old_z + z_coord
    new_pos = Position(x=new_x, y=new_y, z=new_z)
    sc.goto(new_pos)

    print("Scanner position is:")
    print('x: ', new_pos.x)
    print('y: ', new_pos.y)
    print('z: ', new_pos.z)

def f_abort():
    """
    This functions breaks any movements
    """
    pass


def f_home():
    """
    This function sets "home" current cords.
    """
    from src import Position
    sc.set_settings(position=Position(0, 0, 0, 0))
    print("Scanner at home. Scanner position is:")
    current_position = sc.position()
    print('x: ', current_position.x)
    print('y: ', current_position.y)
    print('z: ', current_position.z)