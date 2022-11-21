from PyQt6.QtCore import Qt, QObject, QModelIndex
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QPushButton, QLabel, QSpinBox, QHBoxLayout, QTableWidget, QHeaderView, QTableView
from typing import List
from pyqt_app import scanner
from src.scanner_utils import f_abort, f_home, f_moving_along_x, f_moving_along_y, f_moving_along_z, f_moving_along_w
import numpy as np
from src import Position
from .QSmartTable import QSmartTableModel, Variable, Length
from typing import Union, Type, Any
from PyQt6.QtGui import QColor, QValidator
import re


class MeshTableModel(QSmartTableModel):
    """
    класс, обеспечивающий проверку значений в таблице
    """
    def __init__(self, headers, v_headers, parent: QObject = None, ):
        super(QSmartTableModel, self).__init__()
        self.variable = Variable(name="", default_value=0, type=float, unit=Length, description="")
        self._data = [["" for _ in range(len(headers))] for _ in range(4)]  # добавить None в валидные значения
        self.headers = headers
        self.v_headers = v_headers
        self.pattern = re.compile(r"^\d+(?:\.\d+)?\s*(?:\[\s*[a-zA-Z]*\s*])?$")

    def headerData(self, section: int, orientation: Qt.Orientation, role: int = ...) -> Any:
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                return self.headers[section]
            else:
                return self.v_headers[section]

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        row = index.row()
        column = index.column()
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            return self._data[row][column]
        elif role == Qt.ItemDataRole.BackgroundRole:
            if self._data[row][column] == "":
                return QColor('lightgrey')
            elif self._valid(self._data[row][column], self.variable):
                return
            return QColor('red')

    def flags(self, index: QModelIndex) -> Qt.ItemFlag:
        flags = Qt.ItemFlag.ItemIsSelectable | Qt.ItemFlag.ItemIsEnabled
        flags |= Qt.ItemFlag.ItemIsEditable
        return flags

    def setData(self, index: QModelIndex, value: Any, role: int = ...) -> bool:
        if role == Qt.ItemDataRole.EditRole:
            row = index.row()
            column = index.column()
            self._data[row][column] = value
            self.dataChanged.emit(index, index)
        return True


class MeshTable(QTableView):
    """
    Реализация умной таблицы
    """

    def __init__(self, header: List[str], v_header: List[str], parent: QWidget = None):
        super(MeshTable, self).__init__(parent)
        self.header = header
        self.v_header = v_header
        self.setModel(MeshTableModel(header, v_header, parent))

        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setStretchLastSection(True)


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
        button_x = QPushButton("X")
        button_y = QPushButton("Y")
        button_Z = QPushButton("Z")
        button_w = QPushButton("W")
        button_go = QPushButton("Go")
        self.control_keys_V = ["Begin coordinates [mm]", "End coordinates [mm]", "Step [mm]", "Order"]
        self.control_keys_H = ["X", "Y", "Z", "W"]

        self.x_coord = QLabel(self)
        self.y_coord = QLabel(self)
        self.Z_coord = QLabel(self)
        self.w_coord = QLabel(self)

        self.x_coord.setText("X = ")
        self.y_coord.setText("Y = ")
        self.Z_coord.setText("Z = ")
        self.w_coord.setText("w = ")

        arrow_window_x = QSpinBox(self)  # ввод координаты
        arrow_window_y = QSpinBox(self)  # ввод координаты
        arrow_window_Z = QSpinBox(self)  # ввод координаты
        arrow_window_w = QSpinBox(self)  # ввод координаты

        arrow_window_x.setRange(-1000, 1000)
        arrow_window_y.setRange(-1000, 1000)
        arrow_window_Z.setRange(-1000, 1000)
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

        layout_Z = QHBoxLayout()
        widget_Z = QWidget()
        widget_Z.setLayout(layout_Z)
        layout_Z.addWidget(arrow_window_Z)
        layout_Z.addWidget(button_Z)

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
        self.tableWidget = MeshTable(self.control_keys_H, self.control_keys_V, self)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableWidget.setFixedHeight(200)

        layout_widget = QVBoxLayout()
        widget_coord = QWidget()
        widget_coord.setLayout(layout_widget)
        layout_widget.addWidget(self.x_coord)
        layout_widget.addWidget(self.y_coord)
        layout_widget.addWidget(self.Z_coord)
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
        layout.addWidget(widget_Z)  # добавление горизонтального виджета в вертикальный слой
        layout.addWidget(widget_w)  # добавление горизонтального виджета в вертикальный слой

        layout.addWidget(widget_table)  # добавление горизонтального виджета в вертикальный слой

        # определение функционала кнопок
        button_abort.clicked.connect(f_abort)  # Пока еще заглушка
        button_current_pos.clicked.connect(scanner.position)
        scanner.position_signal.connect(self.update_currrent_position)
        button_home.clicked.connect(f_home)
        button_x.clicked.connect(lambda x: f_moving_along_x(arrow_window_x.value()))
        button_y.clicked.connect(lambda x: f_moving_along_y(arrow_window_y.value()))
        button_Z.clicked.connect(lambda x: f_moving_along_z(arrow_window_Z.value()))
        button_w.clicked.connect(lambda x: f_moving_along_w(arrow_window_w.value()))
        button_go.clicked.connect(self.go_table)
        #self.tableWidget.model().index().data().
    def params_to_linspace(self):
        lst_x = []
        lst_y = []
        lst_Z = []
        lst_w = []

        order1 = [self.tableWidget.item(3, _) for _ in range(4)]
        order = [i if i is None else int(i.text()) for i in order1]

        for _ in range(3):
            lst_x.append(self.tableWidget.item(_, self.control_keys_H.index("X")).text())
            lst_y.append(self.tableWidget.item(_, self.control_keys_H.index("Y")).text())
            lst_Z.append(self.tableWidget.item(_, self.control_keys_H.index("Z")).text())
            lst_w.append(self.tableWidget.item(_, self.control_keys_H.index("W")).text())


        lst_x = [int(i) for i in lst_x]
        lst_y = [int(i) for i in lst_y]
        lst_Z = [int(i) for i in lst_Z]
        lst_w = [int(i) for i in lst_w]

        arr_x = int(abs(lst_x[0] - lst_x[1] - 1) / lst_x[2])  # шаг сетки x
        x = np.linspace(lst_x[0], lst_x[1], arr_x)

        arr_y = int(abs(lst_y[0] - lst_y[1] - 1) / lst_y[2])  # шаг сетки y
        y = np.linspace(lst_y[0], lst_y[1], arr_y)

        arr_Z = int(abs(lst_Z[0] - lst_Z[1] - 1) / lst_Z[2])  # шаг сетки Z
        z = np.linspace(lst_Z[0], lst_Z[1], arr_Z)

        arr_w = int(abs(lst_w[0] - lst_w[1] - 1) / lst_w[2])  # шаг сетки w
        w = np.linspace(lst_w[0], lst_w[1], arr_w)

        return x, y, z, w, order

    def go_table(self):
        """
        This function makes movement by coords from table
        """
        #  здесь вызов конвертации параметров из таблицы в списки

        keys_str = {
            1: self.control_keys_H[0],
            2: self.control_keys_H[1],
            3: self.control_keys_H[2],
            4: self.control_keys_H[3]
        }

        x, y, z, w, order = self.params_to_linspace()

        keys = {
            1: x,
            2: y,
            3: z,
            4: w,
        }

        self.do_line([keys[i] for i in order], "".join([keys_str[i] for i in order]))   # вызов функции следования
                                                                                        # по координатам в соответствии с
                                                                                        # порядком

    def do_line(self, coords: List[np.array], order: str, current_position: List = None):
        if current_position is None:
            current_position = []
        if len(coords) > 1:
            for coord in coords[0]:
                self.do_line(coords[1:], order, [*current_position, coord])
        else:
            for coord in coords[0]:
                temp_coord = [*current_position, coord]
                temp_doc = {order[i]: temp_coord[i] for i in range(len(order))}
                new_pos = Position(**temp_doc)
                scanner.goto(new_pos)
                self.measurements()  # пока заглушка. надо сделать чтобы измеряла что-то в точке
                print(temp_doc)

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
        self.x_coord.setText(f"X = {position.x}")
        self.y_coord.setText(f"Y = {position.y}")
        self.Z_coord.setText(f"Z = {position.z}")
        self.w_coord.setText(f"W = {position.w}")


