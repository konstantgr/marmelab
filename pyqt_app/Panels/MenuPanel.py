from PyQt6.QtWidgets import QMenuBar


class MenuPanel(QMenuBar):
    def __init__(self):
        super(MenuPanel, self).__init__()
        self.add_menu = self.addMenu("File")
        #self.add_menu.addAction()