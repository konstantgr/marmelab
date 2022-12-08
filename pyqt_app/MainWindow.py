from PyQt6.QtWidgets import QWidget, QHBoxLayout, QMainWindow, QSplitter, QTextEdit
from PyQt6.QtCore import Qt
from Panels import LogPanel, RightPanel
# TODO: сделать вывод логов в файл
# TODO: Изменить таблицу сканнер сеттингс
# TODO: Реализация таблицы сканнер контрол (добавить пока что хождение по точкам)
# TODO: ТАблица с настройками объекта и комнаты в рум сеттингс
# TODO: добавить вкладку с настройками комнаты (таблица/поля, размер комнаты в метрах (x, y ,z),
#  область сканирования (x, y, z) и ее пространственная ориенатция (x, y, z), кнопка apply(pass) )
# TODO: убрать лямбда функции
# TODO: вкладка Next --> Test. реализация кнопки Go, которая измеряет и выдает данные
# TODO: ПОСЛЕ ЧЕТВЕРГА
# TODO: добавить в таблицу ск. контролл измерение и запись данных
# TODO: аналогично во вкладке тест


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.main_widget = QWidget()
        hbox = QHBoxLayout(self.main_widget)  # layout of Main window
        self.main_widget.setLayout(hbox)

        self.left_panel = QTextEdit('left_panel', self.main_widget)  # settings selector
        self.center_panel = QTextEdit('center_panel', self.main_widget)  # settings menu

        self.right_panel = RightPanel(
            scanner_visualizer=QTextEdit('сканер'),
            analyzer_visualizer=QTextEdit('анализатор'),
            parent=self.main_widget
        )  # graphics

        self.log_panel = LogPanel(
            parent=self.main_widget
        )  # log window

        # self.left_panel.leftlist.currentRowChanged.connect(self.center_panel.display)
        # room_settings = self.center_panel.room_settings
        # room_settings.settings_signal.connect(self.right_panel.scanner_widget.set_settings_from_dict)

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
        log_splitter.setStretchFactor(0, 4)
        log_splitter.setStretchFactor(1, 1)
        log_splitter.setCollapsible(0, False)
        log_splitter.setCollapsible(1, False)

        main_splitter = QSplitter(orientation=Qt.Orientation.Horizontal)
        main_splitter.insertWidget(0, log_splitter)
        main_splitter.insertWidget(1, self.right_panel)

        main_splitter.setStretchFactor(0, 1)
        main_splitter.setStretchFactor(1, 1)
        main_splitter.setCollapsible(0, False)
        main_splitter.setCollapsible(1, False)

        hbox.addWidget(main_splitter)

        self.setGeometry(300, 300, 450, 400)
        self.setWindowTitle('Scanner control')
        self.setCentralWidget(self.main_widget)
