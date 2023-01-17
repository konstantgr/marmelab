from PyQt6.QtWidgets import QMenuBar, QPushButton
from PyQt6.QtGui import QIcon, QAction
from src.project.icons import info
class MenuPanel(QMenuBar):
    def __init__(self):
        super(MenuPanel, self).__init__()
        self.add_menu = self.addMenu("File")
        #self.add_menu.addAction()
        self.info_menu = self.addMenu("Info")
        self.info_button = QAction(info, "Info")  # добавить кнопку с картинкой
        self.info_menu.addAction(self.info_button)
