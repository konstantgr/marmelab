from MainWindow_class import *

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


app = QApplication(sys.argv)
window = MainWindow()
window.setGeometry(300, 300, 900, 600)

window.button_maker('scanner cont', 'Connect', 100, 15, 'This button makes connections to the scanner', 100, 75)
self.the_button_was_clicked

window.button_maker('scanner cont', 'Move scanner', 100, 100, 'This button makes connections to the scanner', 100, 75)
window.the_button_was_clicked

window.show()

app.exec()