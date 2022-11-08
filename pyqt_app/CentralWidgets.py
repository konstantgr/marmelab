from src.scanner import BaseAxes
from TRIM import DEFAULT_SETTINGS
from pyqt_app import scanner
from src.scanner_utils import f_home, f_X_positive, f_go_table, f_abort, f_connection
from PyQt6.QtWidgets import QPushButton, QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtWidgets import QLabel, QSpinBox, QTableWidget, QHeaderView, QTableWidgetItem
from PyQt6.QtCore import Qt

import logging
logger = logging.getLogger()
logger_print = logging.getLogger()


class Init(QWidget):
    """

    """
    def __init__(self):
        super().__init__()
        """
        This function makes connection to the scanner
        """
        layout = QHBoxLayout()
        self.setLayout(layout)
        button = QPushButton("Connect")
        layout.addWidget(button)
        button.clicked.connect(f_connection)


class QSettingsTableWidget(QTableWidget):
    def __init__(self, *args, **kwargs):
        super(QSettingsTableWidget, self).__init__(*args, **kwargs)


class RoomSettings(QWidget):
    def __init__(self):
        super(RoomSettings, self).__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)


class ScannerSettings(QWidget):
    """

    """
    def __init__(self):
        super(ScannerSettings, self).__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.button_apply = QPushButton("Apply")
        self.button_default_set = QPushButton("Default settings")  # должны подтягивать настройки с трим сканнера

        self.button_apply.clicked.connect(self.apply_settings)
        self.button_default_set.clicked.connect(self.set_default_settings)

        # формирование таблицы

        self.settings_keys = {
            'acceleration': "Acceleration",
            'deceleration': "Deceleration",
            'velocity': "Velocity",
            'motion_mode': "Motion mode",
            'special_motion_mode': "Special motion mode",
            'motor_on': "Motor on / off"
        }

        self.table_widget = QTableWidget(len(self.settings_keys), 4)
        self.table_widget.setColumnWidth(0, 50)
        self.table_widget.setColumnWidth(1, 50)
        self.table_widget.setColumnWidth(2, 50)
        self.table_widget.setColumnWidth(3, 50)
        self.table_widget.setVerticalHeaderLabels(self.settings_keys.values())
        self.table_widget.setHorizontalHeaderLabels(("X", "Y", "Z", "W"))
        self.table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table_widget.setFixedHeight(300)

        self.layout().addWidget(self.table_widget)
        self.layout().addWidget(self.button_apply)
        self.layout().addWidget(self.button_default_set)

    def settings_to_dict(self):
        user_settings = {}
        for key, value in DEFAULT_SETTINGS.items():
            #logger.info(f"{key}")
            j = list(self.settings_keys.keys()).index(key)
            cl = value.__class__ if isinstance(value.__class__, BaseAxes) else BaseAxes
            x = self.table_widget.item(j, 0)
            y = self.table_widget.item(j, 1)
            z = self.table_widget.item(j, 2)
            w = self.table_widget.item(j, 3)

            user_settings[key] = cl(
                x=x if x is None else float(x.text()),
                y=y if y is None else float(y.text()),
                z=z if z is None else float(z.text()),
                w=w if w is None else float(w.text()),
            )
        return user_settings

    def set_default_settings(self):
        for j, key in enumerate(self.settings_keys):
            setting = DEFAULT_SETTINGS.get(key)

            if isinstance(setting, BaseAxes):
                x, y, z, w = setting.x, setting.y, setting.z, setting.w
            else:
                x = y = z = w = setting.A
            self.table_widget.setItem(j, 0, QTableWidgetItem(str(x)))
            self.table_widget.setItem(j, 1, QTableWidgetItem(str(y)))
            self.table_widget.setItem(j, 2, QTableWidgetItem(str(z)))
            self.table_widget.setItem(j, 3, QTableWidgetItem(str(w)))

    def apply_settings(self):
        scanner.set_settings(**self.settings_to_dict())


class ScannerControl(QWidget):
    """

    """

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        button_abort = QPushButton("Abort")
        button_current_pos = QPushButton("Current position is..")
        button_home = QPushButton("Home")
        button_x = QPushButton("x")
        button_y = QPushButton("y")
        button_z = QPushButton("z")
        button_w = QPushButton("w")
        button_go = QPushButton("Go")
        self.x_coord = QLabel(self)
        self.y_coord = QLabel(self)
        self.z_coord = QLabel(self)
        self.w_coord = QLabel(self)

        self.x_coord.setText("x = ")
        self.y_coord.setText("y = ")
        self.z_coord.setText("z = ")
        self.w_coord.setText("w = ")

        arrow_window_x = QSpinBox(self)  #ввод координаты
        arrow_window_y = QSpinBox(self)  #ввод координаты
        arrow_window_z = QSpinBox(self)  #ввод координаты
        arrow_window_w = QSpinBox(self)  #ввод координаты

        arrow_window_x.setRange(-17*10 ** 6, 17 * 10 ** 6)
        arrow_window_y.setRange(-10 ** 6, 10 ** 6)
        arrow_window_z.setRange(-2500000, 2500000)
        arrow_window_w.setRange(-100000, 100000)

        #  создание горизонтального слоя внутри вертикального для окна с выбором значения координаты и кнопки перемещения по оси х по заданной координате
        layout_x = QHBoxLayout()
        widget_x = QWidget()
        widget_x.setLayout(layout_x)
        layout_x.addWidget(arrow_window_x)
        layout_x.addWidget(button_x)

        layout_y = QHBoxLayout()
        widget_y = QWidget()
        widget_y.setLayout(layout_y)
        layout_y.addWidget(arrow_window_y)
        layout_y.addWidget(button_y)

        layout_z = QHBoxLayout()
        widget_z = QWidget()
        widget_z.setLayout(layout_z)
        layout_z.addWidget(arrow_window_z)
        layout_z.addWidget(button_z)

        layout_w = QHBoxLayout()
        widget_w = QWidget()
        widget_w.setLayout(layout_w)
        layout_w.addWidget(arrow_window_w)
        layout_w.addWidget(button_w)


        #  создание горизонтального слоя внутри вертикального для помещения туда таблицы и кнопок пуск и аборт
        layout_table = QHBoxLayout()
        widget_table = QWidget()
        widget_table.setLayout(layout_table)
        layout_table.setAlignment(Qt.AlignmentFlag.AlignTop)
        # формирование таблицы, в которой задаются значения координат, скоростей и шага для трех осей
        tableWidget = QTableWidget(4, 3)
        tableWidget.setHorizontalHeaderLabels(("Begin coord.", "End coord.", "Step"))
        tableWidget.setVerticalHeaderLabels(("X", "Y", "Z", "W"))
        tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        #tableWidget.setFixedSize(150, 150)

        layout_widget = QVBoxLayout()
        widget_coord = QWidget()
        widget_coord.setLayout(layout_widget)
        layout_widget.addWidget(self.x_coord)
        layout_widget.addWidget(self.y_coord)
        layout_widget.addWidget(self.z_coord)
        layout_widget.addWidget(self.w_coord)

        layout_go_abort = QHBoxLayout()
        widget_go_abort  = QWidget()
        widget_go_abort .setLayout(layout_go_abort )
        layout_go_abort.addWidget(button_go)
        layout_go_abort.addWidget(button_abort)

        layout_widget.addWidget(widget_go_abort)

        layout_table.addWidget(tableWidget)
        layout_table.addWidget(widget_coord)

        # добавление всех виджетов в основной слой
        layout.addWidget(button_home)
        layout.addWidget(button_current_pos)
        layout.addWidget(widget_x)  # добавление горизонтального виджета в вертикальный слой
        layout.addWidget(widget_y)  # добавление горизонтального виджета в вертикальный слой
        layout.addWidget(widget_z)  # добавление горизонтального виджета в вертикальный слой
        layout.addWidget(widget_w)  # добавление горизонтального виджета в вертикальный слой


        layout.addWidget(widget_table)  # добавление горизонтального виджета в вертикальный слой


        # определение функционала кнопок
        button_abort.clicked.connect(f_abort)  #заглушка
        button_current_pos.clicked.connect(self.update_currrent_position)
        button_home.clicked.connect(f_home)
        button_x.clicked.connect(lambda x: f_X_positive(arrow_window_x.value()))

        #  КОСТЫЛЬ! переделать
        button_go.clicked.connect(
            lambda x: f_go_table(int(tableWidget.item(0, 0).text()),
                                 int(tableWidget.item(1, 0).text()),
                                 int(tableWidget.item(2, 0).text()),
                                 int(tableWidget.item(3, 0).text())))

    def update_currrent_position(self):
        """
        This function shows current position
        """
        current_position = scanner.position()
        self.x_coord.setText(f"x = {current_position.x}")
        self.y_coord.setText(f"y = {current_position.y}")
        self.z_coord.setText(f"z = {current_position.z}")
        self.w_coord.setText(f"w = {current_position.w}")
        # print('x: ', current_position.x)
        # print('y: ', current_position.y)
        # print('z: ', current_position.z)


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