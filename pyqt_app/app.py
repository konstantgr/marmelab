from MainWindow import MainWindow
from pyqt_app import app


if __name__ == "__main__":
    window = MainWindow()
    window.setGeometry(300, 300, 900, 600)
    window.show()
    app.exec()
