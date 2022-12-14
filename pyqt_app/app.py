from MainWindow import MainWindow
from pyqt_app import app


if __name__ == "__main__":
    window = MainWindow()
    #tool_bar = window.addToolBar("s")
    #tool_bar.addAction(icon=unnamed.png)
    window.setGeometry(300, 300, 900, 600)
    window.show()
    app.exec()
