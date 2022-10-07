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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setGeometry(300, 300, 900, 600)
    window.button_maker('scanner cont', 'Connect', 675, 15, 'This button makes connections to the scanner', 100, 75,
                        scanner_utils.f_connection) # The button connect
    window.button_maker('scanner cont', 'Up', 700, 100, 'This button makes connections to the scanner', 40, 40,
                        scanner_utils.f_connection1) # The button Up for 1 mm

    window.button_maker('scanner cont', 'Down', 700, 150, 'This button makes connections to the scanner', 40, 40,
                        scanner_utils.f_connection1) # The button Down for 1 mm

    window.button_maker('scanner cont', 'Left', 650, 125, 'This button makes connections to the scanner', 40, 40,
                        scanner_utils.f_connection1) # The button Left for 1 mm

    window.button_maker('scanner cont', 'Right', 750, 125, 'This button makes connections to the scanner', 40, 40,
                        scanner_utils.f_connection1) # The button Right for 1 mm

    # window.button_maker('scanner cont', 'Move scanner', 100, 100, 'This button makes connections to the scanner', 100, 75)
    # window.the_button_was_clicked
    window.show()

    app.exec()