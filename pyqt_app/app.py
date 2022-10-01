import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QPushButton,
                             QGridLayout, QWidget, QHBoxLayout, QVBoxLayout)
sys.path.append('..')
from src.matmul import random_matmul
from time import time


class Window(QWidget):
    def __init__(self):
        super().__init__()
        buttons = {
            'TOP': QPushButton("TOP"),
            # 'CENTER': QPushButton("CENTER"),
            'LEFT': QPushButton("LEFT"),
            'RIGHT': QPushButton("RIGHT"),
            'BOTTOM': QPushButton("BOTTOM"),
        }
        positions_mapping = {
            'TOP': (0, 1),
            # 'CENTER': (1, 1),
            'LEFT': (1, 0),
            'RIGHT': (1, 2),
            'BOTTOM': (2, 1),
        }

        layout = QGridLayout()
        for key, btn in buttons.items():
            btn.clicked.connect(lambda _, key=key: self.moving(key))
            layout.addWidget(btn, *positions_mapping[key])

        self.setLayout(layout)

    def moving(self, key):
        print(f"MOVING {key}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = Window()
    window.show()

    sys.exit(app.exec())
