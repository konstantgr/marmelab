from MainWindow_class import *
from src import scanner_utils

if __name__ == "__main__":
    sc = None
    app = QApplication(sys.argv)
    window = MainWindow()
    window.setGeometry(300, 300, 900, 600)
    window.show()
    app.exec()
