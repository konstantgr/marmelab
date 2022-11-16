from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSpinBox, QHBoxLayout, QTableWidget, QHeaderView
from typing import List
from pyqt_app import scanner
from src.scanner_utils import f_abort, f_home, f_X_positive
import numpy as np
from src import Position


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

        arrow_window_x = QSpinBox(self)  # ввод координаты
        arrow_window_y = QSpinBox(self)  # ввод координаты
        arrow_window_z = QSpinBox(self)  # ввод координаты
        arrow_window_w = QSpinBox(self)  # ввод координаты

        arrow_window_x.setRange(-1000, 1000)
        arrow_window_y.setRange(-1000, 1000)
        arrow_window_z.setRange(-1000, 1000)
        arrow_window_w.setRange(-1000, 1000)

        # создание горизонтального слоя внутри вертикального для окна с выбором значения координаты и
        # кнопки перемещения по оси х по заданной координате
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

        # создание горизонтального слоя внутри вертикального для помещения туда таблицы и кнопок пуск и аборт
        layout_table = QHBoxLayout()
        widget_table = QWidget()
        widget_table.setLayout(layout_table)
        layout_table.setAlignment(Qt.AlignmentFlag.AlignTop)
        # формирование таблицы, в которой задаются значения координат, скоростей и шага для трех осей

        self.control_keys_V = ["Begin coordinates", "End coordinates", "Step", "Order"]
        self.control_keys_H = ["X", "Y", "Z", "W"]

        self.tableWidget = QTableWidget(len(self.control_keys_V), 4)
        self.tableWidget.setVerticalHeaderLabels(self.control_keys_V)
        self.tableWidget.setHorizontalHeaderLabels(self.control_keys_H)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableWidget.setFixedHeight(200)

        layout_widget = QVBoxLayout()
        widget_coord = QWidget()
        widget_coord.setLayout(layout_widget)
        layout_widget.addWidget(self.x_coord)
        layout_widget.addWidget(self.y_coord)
        layout_widget.addWidget(self.z_coord)
        layout_widget.addWidget(self.w_coord)

        layout_go_abort = QHBoxLayout()
        widget_go_abort = QWidget()
        widget_go_abort.setLayout(layout_go_abort)
        layout_go_abort.addWidget(button_go)
        layout_go_abort.addWidget(button_abort)

        layout_widget.addWidget(widget_go_abort)

        layout_table.addWidget(self.tableWidget)
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
        button_abort.clicked.connect(f_abort)  # Пока еще заглушка
        button_current_pos.clicked.connect(scanner.position)
        scanner.position_signal.connect(self.update_currrent_position)
        button_home.clicked.connect(f_home)
        button_x.clicked.connect(lambda x: f_X_positive(arrow_window_x.value()))
        button_go.clicked.connect(self.go_table)

    def params_to_dict(self):
        dic = {"X": [], "Y": [], "Z": [], "W": []}
        lst_x = []
        lst_y = []
        lst_z = []
        lst_w = []

        order1 = [self.tableWidget.item(3, _) for _ in range(4)]
        order = [i if i is None else int(i.text()) for i in order1]

        for _ in range(3):
            lst_x.append(self.tableWidget.item(_, self.control_keys_H.index("X")).text())
            lst_y.append(self.tableWidget.item(_, self.control_keys_H.index("Y")).text())
            lst_z.append(self.tableWidget.item(_, self.control_keys_H.index("Z")).text())
            lst_w.append(self.tableWidget.item(_, self.control_keys_H.index("W")).text())

        dic["X"] = lst_x
        dic["Y"] = lst_y
        dic["Z"] = lst_z
        dic["W"] = lst_w
        print(dic, order)
        return dic, order

    def go_table(self):
        """
        This function makes movement by coords from table
        """
        #  здесь вызов конвертации параметров из таблицы в списки
        #  здесь нет связи с self.control_keys_H. если там что-то изменится, нельзя будет отследить


        control_keys = {
            1: self.control_keys_H[0],
            2: self.control_keys_H[1],
            3: self.control_keys_H[2],
            4: self.control_keys_H[3]
        }

        dic, order = self.params_to_dict()
        print(dic.get(control_keys.get(order[0])))
        self.movement(dic.get(control_keys.get(order[0])), order[0])
        self.movement(dic.get(control_keys.get(order[1])), order[1])
        self.movement(dic.get(control_keys.get(order[2])), order[2])
        self.movement(dic.get(control_keys.get(order[3])), order[3])

    def movement(self, lst:List, order):
        print(lst)
        if order == self.control_keys_H[0]:
            start = float(lst[0])
            end = float(lst[1])
            step = float(lst[2])

            new_pos = Position(x=start)
            scanner.goto(new_pos)

            arr = int(abs(start - end - 1) / step)
            a = np.linspace(start, end, arr)

            # попытка сделать отображения точек при каждом изменении координат
            for i in a:
                print(i)
                new_pos = Position(x=i)
                scanner.goto(new_pos)
                current_position = scanner.position()
                self.measurements()
                self.x_coord.setText(f"x = {current_position.x}")  # виснет
                self.y_coord.setText(f"y = {current_position.y}")
                self.z_coord.setText(f"z = {current_position.z}")
                self.w_coord.setText(f"w = {current_position.w}")

        elif order == self.control_keys_H[1]:
            start = float(lst[0])
            end = float(lst[1])
            step = float(lst[2])

            new_pos = Position(y=start)
            scanner.goto(new_pos)

            arr = int(abs(start - end - 1) / step)
            a = np.linspace(start, end, arr)

            for i in a:
                new_pos = Position(y=i)
                scanner.goto(new_pos)
                self.measurements()

        elif order == self.control_keys_H[2]:
            start = float(lst[0])
            end = float(lst[1])
            step = float(lst[2])

            new_pos = Position(z=start)
            scanner.goto(new_pos)

            arr = int(abs(start - end - 1) / step)
            a = np.linspace(start, end, arr)

            for i in a:
                new_pos = Position(z=i)
                scanner.goto(new_pos)
                self.measurements()

        elif order == self.control_keys_H[3]:
            start = float(lst[0])
            end = float(lst[1])
            step = float(lst[2])

            new_pos = Position(w=start)
            scanner.goto(new_pos)

            arr = int(abs(start - end - 1) / step)
            a = np.linspace(start, end, arr)

            for i in a:
                new_pos = Position(w=i)
                scanner.goto(new_pos)
                self.measurements()

    def measurements(self):
        """
        функция-заглушка. вместо нее надо функцию измерения сделать
        :return:
        """
        pass

    def update_currrent_position(self, position: Position):
        """
        This function shows current position
        """
        self.x_coord.setText(f"x = {position.x}")
        self.y_coord.setText(f"y = {position.y}")
        self.z_coord.setText(f"z = {position.z}")
        self.w_coord.setText(f"w = {position.w}")


