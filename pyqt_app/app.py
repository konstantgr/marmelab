from MainWindow_class import *
from src import scanner_utils

"""
Описание работы функции, которая делает кнопки
1 аргумент текст над кнопкой
2 аргумент имя кнопки
3 аргумент координата кнопки по х
4 аргумент координата кнопки по у
5 аргумент текст всплывающего окна
6 аргумент размер кнопки по х
7 аргумент размер кнопки по у
"""
# TODO: Реализовать управление сканнером через окошки,
#  в которые можно вбивать координаты,
# TODO: Реализовать поля, в которых отображаются координаты
# TODO: Реализовать кнопку Аборт

if __name__ == "__main__":
    sc = None
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setGeometry(300, 300, 900, 600)
    window.button_maker('scanner cont', 'Connect', 670, 15, 'This button makes connections to the scanner', 100, 55,
                        scanner_utils.f_connection) # The button connect
    window.button_maker('scanner cont', 'Up', 700, 100, 'This button makes movement upward', 40, 40,
                        scanner_utils.f_up) # The button Up for 1 mm

    # window.button_maker('scanner cont', 'Down', 700, 150, 'This button makes movement down', 40, 40,
    #                     scanner_utils.f_down) # The button Down for 1 mm
    #
    # window.button_maker('scanner cont', 'Left', 650, 125, 'This button makes connections to the left', 40, 40,
    #                     scanner_utils.f_default) # The button Left for 1 mm
    #
    # window.button_maker('scanner cont', 'Right', 750, 125, 'This button makes connections to the right', 40, 40,
    #                     scanner_utils.f_right) # The button Right for 1 mm


    window.button_maker('scanner cont', 'Currrent position is..', 665, 200, 'This button shows current coordinates', 120, 25,
                        scanner_utils.f_currrent_position) # The button connect

    window.button_maker('scanner cont', 'Abort', 665, 230, 'This button aborts current movements',
                        120, 25,
                        scanner_utils.f_currrent_position)  # The button connect

    #
    # window.button_maker('scanner cont', 'Axes X', 300, 230, 'This button aborts current movements',
    #                      120, 25,
    #                      scanner_utils.f_currrent_position)  # The button connect
    #
    #

    window.text_on_the_window("Axes X", 708, 270)
    window.field_text_button(710, 300, 30, 30)
    window.button_maker('scanner cont', '+', 750, 300, 'This button makes movement in positive direction',
                        30, 30,
                        scanner_utils.f_X_positive(10))
    window.button_maker('scanner cont', '-', 670, 300, 'This button makes movement in negative direction',
                        30, 30,
                        scanner_utils.f_default)


    window.text_on_the_window("Axes Y", 708, 330)
    window.field_text_button(710, 360, 30, 30)
    window.button_maker('scanner cont', '+', 750, 360, 'This button makes movement in positive direction',
                        30, 30,
                        scanner_utils.f_default)
    window.button_maker('scanner cont', '-', 670, 360, 'This button makes movement in negative direction',
                        30, 30,
                        scanner_utils.f_default)



    window.text_on_the_window("Axes Z", 708, 390)
    window.field_text_button(710, 420, 30, 30)
    window.button_maker('scanner cont', '+', 750, 420, 'This button makes movement in positive direction',
                        30, 30,
                        scanner_utils.f_currrent_position)
    window.button_maker('scanner cont', '-', 670, 420, 'This button makes movement in negative direction',
                        30, 30,
                        scanner_utils.f_currrent_position)



    window.show()
    app.exec()
