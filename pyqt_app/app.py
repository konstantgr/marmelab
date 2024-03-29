from MainWindow import MainWindow
from pyqt_app import app, builder


STYLE_SHEET = """
QPushButton {
    background-color: #E1E1E1;
    border: 1px solid #ADADAD;
    border-radius: 2px;
    color: 161616;
    padding: 3px 5px;
    width: 150px;
}
QPushButton:hover {
    background-color: #E1E8F4;
}
QPushButton:disabled {
    border-color: #999999;
    background-color: #C4C4C4;
    color: #6B6B6B;
}
QPushButton[color='red'] {
    background-color: #FF3232;
}
QSplitter[type='inner']::handle {
    image: url(assets/Untitled.png);
}
QGroupBox[type='toolbar'] {
    border: none;
    margin-bottom: 7px;
}
QGroupBox[type='toolbar']::title {
    subcontrol-origin:  margin;
    subcontrol-position: bottom center;
    color: gray;
}
"""


if __name__ == "__main__":
    window = MainWindow()
    window.setGeometry(300, 300, 900, 600)
    window.show()
    app.setStyleSheet(STYLE_SHEET)
    app.exec()
