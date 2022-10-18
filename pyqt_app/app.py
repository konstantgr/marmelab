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
    window.button_maker( 'Connect', 670, 15, 'This button makes connections to the scanner', 100, 55,
                        scanner_utils.f_connection)
    window.button_maker( 'Up', 700, 120, 'This button makes movement upward', 40, 40,
                        scanner_utils.f_up)

    window.button_maker( 'Currrent position is..', 665, 200, 'This button shows current coordinates', 120, 25,
                        scanner_utils.f_currrent_position)

    window.button_maker( 'Abort', 665, 230, 'This button aborts current movements',
                        120, 25, scanner_utils.f_abort)

    window.button_maker('Home', 665, 75, 'This button defines home',
                        120, 25, scanner_utils.f_home)


    window.text_on_the_window("Axes X", 708, 270)
    window.field_text_button(710, 300, 30, 30)
    # TODO:!!!
    window.button_maker('+', 750, 300, 'This button makes movement in positive direction',
                        30, 30, scanner_utils.f_X_positive)
    window.button_maker('-', 670, 300, 'This button makes movement in negative direction',
                        30, 30, scanner_utils.f_default)


    window.text_on_the_window("Axes Y", 708, 330)
    window.field_text_button(710, 360, 30, 30)
    window.button_maker('+', 750, 360, 'This button makes movement in positive direction',
                        30, 30, scanner_utils.f_default)
    window.button_maker('-', 670, 360, 'This button makes movement in negative direction',
                        30, 30, scanner_utils.f_default)



    window.text_on_the_window("Axes Z", 708, 390)
    a = window.field_text_button(710, 420, 30, 30)
    a.setPlainText("123")
    print(a)
    window.button_maker('+', 750, 420, 'This button makes movement in positive direction',
                        30, 30, scanner_utils.f_Z_positive)
    window.button_maker('-', 670, 420, 'This button makes movement in negative direction',
                        30, 30, scanner_utils.f_default)



    window.show()
    app.exec()
