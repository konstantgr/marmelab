from ..Project import PWidget, PPath
from PyQt6.QtWidgets import QTextEdit, QWidget, QHBoxLayout, QHeaderView, QHBoxLayout, QTableView, QVBoxLayout
import numpy as np
from dataclasses import dataclass, field
from typing import List
from ..Widgets.SettingsTable import QSmartTableModel, Variable
from PyQt6.QtCore import Qt, QObject, QModelIndex
from PyQt6.QtGui import QColor
from typing import Any
from pyqt_app import project
from src.project.Widgets import StateDepPushButton
import re


class Settings(QWidget):
    def __init__(self):
        super(Settings, self).__init__('')
        #добавить экземпляр класса таблицы


class MeshTableModel(QSmartTableModel):
    """
    класс, обеспечивающий проверку значений в таблице
    """
    def __init__(self, headers, v_headers, parent: QObject = None, ):
        super(QSmartTableModel, self).__init__()
        self.variable = Variable(name="", default_value=0, type=float, description="")
        #self.variable = Variable(name="", default_value=0, type=float, unit=Length, description="")  реализовать валидацию
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


class ScannerControlTable(QWidget):
    """
    """

    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.setLayout(layout)
        self.button_go = StateDepPushButton(
            state=project.scanner.states.is_connected,
            text="Go",
            parent=self
        )

        self.control_keys_V = ["Begin coordinates", "End coordinates", "Step", "Order"]
        self.control_keys_H = ["x", "y", "z", "w"]

        # создание горизонтального слоя внутри вертикального для окна с выбором значения координаты и
        # кнопки перемещения по оси х по заданной координате

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

        layout.addWidget(widget_table)  # добавление горизонтального виджета в вертикальный слой
        self.button_go.clicked.connect(self.go_table)



    def params_to_linspace(self):
        lst_x = []
        lst_y = []
        lst_z = []
        lst_w = []
        order1 = []

        x, y, z, w = [], [], [], []

        for _ in range(4):
            order1.append((self.tableWidget.model().index(3, _).data()))

        order = [int(i) for i in order1 if i.isdigit()]
        print(order)
        #  реализация считывания данных в таблице

        for _ in range(3):
            lst_x.append(self.tableWidget.model().index(_, self.control_keys_H.index("x")).data())
            lst_y.append(self.tableWidget.model().index(_, self.control_keys_H.index("y")).data())
            lst_z.append(self.tableWidget.model().index(_, self.control_keys_H.index("z")).data())
            lst_w.append(self.tableWidget.model().index(_, self.control_keys_H.index("w")).data())

        lst_x = [int(float(i)) for i in lst_x if i.isdigit()]
        lst_y = [int(float(i)) for i in lst_y if i.isdigit()]
        lst_z = [int(float(i)) for i in lst_z if i.isdigit()]
        lst_w = [int(float(i)) for i in lst_w if i.isdigit()]

        if len(lst_x) != 0:
            arr_x = int(abs(lst_x[0] - lst_x[1] - 1) / lst_x[2])  # шаг сетки x
            x = np.linspace(lst_x[0], lst_x[1], arr_x)

        if len(lst_y) != 0:
            arr_y = int(abs(lst_y[0] - lst_y[1] - 1) / lst_y[2])  # шаг сетки y
            y = np.linspace(lst_y[0], lst_y[1], arr_y)

        if len(lst_z) != 0:
            arr_z = int(abs(lst_z[0] - lst_z[1] - 1) / lst_z[2])  # шаг сетки Z
            z = np.linspace(lst_z[0], lst_z[1], arr_z)

        if len(lst_w) != 0:
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

        #self.do_line([keys[i] for i in order], "".join([keys_str[i] for i in order]))   # вызов функции следования
                                                                                        # по координатам в соответствии с
                                                                                        # порядком

@dataclass
class Path3d(PPath):
    widget: QWidget = field(default_factory=Settings)
    points: np.ndarray = np.array([])
