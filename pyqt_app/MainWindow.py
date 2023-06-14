from PyQt6.QtWidgets import QWidget, QHBoxLayout, QMainWindow, QSplitter, QTextEdit, QPushButton
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon
from Panels import LogPanel, RightPanel, LeftPanel, CentralPanel, MenuPanel
from Panels.BarPanel import BarPanel
from Panels.ToolPanel import ToolPanel
from pyqt_app import project, builder


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main_widget = QWidget()
        hbox = QHBoxLayout(self.main_widget)  # layout of Main window
        self.main_widget.setLayout(hbox)
        # self.main_widget.setStyleSheet("background-color: red")

        self.tool_panel = ToolPanel(self.main_widget)
        self.addToolBar(self.tool_panel)
        # self.menu_panel = MenuPanel() # меню бар надо тул баром
        # self.setMenuBar(self.menu_panel)

        self.left_panel = LeftPanel(self.main_widget)  # settings selector
        self.center_panel = CentralPanel(self.main_widget)  # settings menu
        self.bar_panel = BarPanel(self.main_widget)  # status bar window

        # self.bar_panel.bar_status_signal.emit("Status scanner")  # отправка в стек сигналов строки "Status scanner"
        #  висит для примера
        self.left_panel.signals.tree_num.connect(self.center_panel.display)

        project.scanner.signals.is_connected.connect(self.bar_panel.sc_status_msg)
        project.scanner.signals.is_connected.emit(project.scanner.instrument.is_connected)

        project.analyzer.signals.is_connected.connect(self.bar_panel.an_status_msg)
        project.analyzer.signals.is_connected.emit(False)

        self.right_panel = RightPanel(
            scanner_visualizer=builder.scanner_visualizer,
            plots_visualizer=builder.plots_visualizer,
            parent=self.main_widget
        )  # graphics

        self.log_panel = LogPanel(
            parent=self.main_widget
        )  # log window

        left_center_splitter = QSplitter(orientation=Qt.Orientation.Horizontal)
        left_center_splitter.insertWidget(0, self.left_panel)
        left_center_splitter.insertWidget(1, self.center_panel)
        left_center_splitter.setStretchFactor(0, 0)
        left_center_splitter.setStretchFactor(1, 1)
        left_center_splitter.setCollapsible(0, False)
        left_center_splitter.setCollapsible(1, False)

        log_splitter = QSplitter(orientation=Qt.Orientation.Vertical)
        log_splitter.insertWidget(0, left_center_splitter)
        log_splitter.insertWidget(1, self.log_panel)
        self.setStatusBar(self.bar_panel)
        log_splitter.setStretchFactor(0, 4)
        log_splitter.setStretchFactor(1, 1)
        log_splitter.setCollapsible(0, False)
        log_splitter.setCollapsible(1, False)

        main_splitter = QSplitter(orientation=Qt.Orientation.Horizontal)
        main_splitter.insertWidget(0, log_splitter)
        main_splitter.insertWidget(1, self.right_panel)

        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 2)
        main_splitter.setCollapsible(0, False)
        main_splitter.setCollapsible(1, False)

        hbox.addWidget(main_splitter)

        self.setGeometry(300, 300, 450, 400)
        self.setWindowTitle('MarMELAB v0.0.2')
        self.setWindowIcon(QIcon("assets/logo.png"))
        self.setCentralWidget(self.main_widget)


