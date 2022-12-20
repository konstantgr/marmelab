from ..Project import PPath
from PyQt6.QtWidgets import QWidget, QHeaderView, QHBoxLayout, QTableView, QVBoxLayout, QPushButton,\
    QSizePolicy, QMenuBar, QTabWidget, QCheckBox, QGroupBox
import numpy as np
from dataclasses import dataclass, field
from typing import List
from ..Widgets.SettingsTable import QSmartTableModel, Variable
from PyQt6.QtCore import Qt, QModelIndex, QObject, QModelIndex
from PyQt6.QtGui import QColor
from typing import Any
from ..Widgets import StateDepPushButton
from ...scanner.TRIM import TRIMScanner
from ..Project import PScannerStates

import re
# TODO: менять в таблице координату конца, или расстояние, на которую надо переместиться
# TODO: менять количесвто измеряемых точек на шаг измерния
# TODO: итого: 4 таблицы, которые надо связать QStacked Widget, signal (по аналогии с тем, что было с панелями раньше)
# TODO: иконки в тул бар QAction, "добавить путь", "добавить объект", "Аборт"


class Path3dWidget(QWidget):
    """
    Класс талбицы
    """
    def __init__(self):

        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        """
        несколько листов в таблице
        self.coord_box = QCheckBox("Relative coordinates")
        self.widget2 = Table1Widget()
        self.widget1 = Table1Widget()
        self.stackWidget = QTabWidget()
        self.stackWidget.addTab(self.widget1, "Step")
        self.stackWidget.addTab(self.widget2, "Split")
        self.layout.addWidget(self.coord_box)
        self.layout.addWidget(self.stackWidget)
        
        """

        self.widget1 = Table1Widget()
        self.layout.addWidget(self.widget1)

class MeshTableModel(QSmartTableModel):
    """
    класс, обеспечивающий проверку значений в таблице
    """
    def __init__(self, headers, v_headers, parent: QObject = None, ):
        super(QSmartTableModel, self).__init__()
        #self.variable = Variable(name="", default_value=0, type=float, description="")
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

    def rowCount(self, parent: QModelIndex = ...) -> int:
        return len(self._data)

    def columnCount(self, parent: QModelIndex = ...) -> int:
        return len(self._data[0])

    def data(self, index: QModelIndex, role: int = ...) -> Any:
        row = index.row()
        column = index.column()
        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            return self._data[row][column]
        elif role == Qt.ItemDataRole.BackgroundRole:
            if self._data[row][column] == "":
                return QColor('lightgrey')
            #elif self._valid(self._data[row][column], self.variable):
                #return
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


class Table1Widget(QWidget):
    def __init__(self):
        super().__init__()
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.hbox = QHBoxLayout()
        self.add_widget = QWidget()
        self.add_widget.setLayout(self.hbox)
        self.group = QGroupBox(self)
        self.group_layout = QVBoxLayout(self.group)


        self.temp_button = QPushButton("Print test button")
        self.temp_button.clicked.connect(self.go_table)  # временная кнопка. Необходимо, чтобы go_table была доступна
                                                    # вне класса - в эксперименте.
        self.temp_button.setProperty('color', 'red')
        self.set_button = QPushButton("Set current coordinates")




        self.hbox.addWidget(self.set_button)
        self.hbox.addWidget(self.temp_button)
        self.control_keys_V = ["Begin coordinates", "End coordinates", "Step", "Order"]
        self.control_keys_H = ["x", "y", "z", "w"]
        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        # формирование таблицы, в которой задаются значения координат, скоростей и шага для трех осей
        self.tableWidget = MeshTable(self.control_keys_H, self.control_keys_V, self)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableWidget.setFixedHeight(200)
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)

        self.hbox.addWidget(self.temp_button)
        self.hbox.addWidget(self.set_button)
        self.hbox.addWidget(self.group)
        self.layout.addWidget(self.add_widget)
        self.layout.addWidget(self.tableWidget)

        self.hbox.setAlignment(Qt.AlignmentFlag.AlignTop)

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
        print(f"x={x}, y={y}, z={z}, w={w}")
        #self.do_line([keys[i] for i in order], "".join([keys_str[i] for i in order]))   # вызов функции следования
                                                                                        # по координатам в соответствии с                                                                                        # порядком



@dataclass
class Path3d(PPath):
    widget: QWidget = field(default_factory=Path3dWidget)
    points: np.ndarray = np.array([])

