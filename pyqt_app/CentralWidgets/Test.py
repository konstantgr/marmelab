from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton


class Test(QWidget):
    def __init__(self):
        super(Test, self).__init__()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.setLayout(layout)
        button_go = QPushButton("Go")
        button_download = QPushButton("Download")
        layout.addWidget(button_go)
        layout.addWidget(button_download)
