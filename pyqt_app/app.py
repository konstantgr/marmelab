import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton
from src.matmul import random_matmul
from time import time


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My App")

        button = QPushButton("Press Me!")
        button.setCheckable(True)
        button.clicked.connect(self.the_button_was_clicked)

        self.setCentralWidget(button)

    def the_button_was_clicked(self):
        start_time = time()
        random_matmul()[0, 0]
        print(time() - start_time)


app = QApplication(sys.argv)

window = MainWindow()
window.show()

app.exec()