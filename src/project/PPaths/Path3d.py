from ..Project import PPath, PScanner
from PyQt6.QtWidgets import QWidget, QHeaderView, QHBoxLayout, QTableView, QVBoxLayout, QPushButton,\
    QSizePolicy, QMenuBar, QTabWidget, QCheckBox, QGroupBox, QComboBox
import numpy as np
from dataclasses import dataclass, field
from typing import List
from ..Widgets.SettingsTable import QSmartTableModel, Variable
from PyQt6.QtCore import Qt, QModelIndex, QObject, QModelIndex
from PyQt6.QtGui import QColor
from typing import Any
from src.project.Widgets import StateDepPushButton

import re
# TODO: менять в таблице координату конца, или расстояние, на которую надо переместиться
# TODO: менять количесвто измеряемых точек на шаг измерния
# TODO: итого: 4 таблицы, которые надо связать QStacked Widget, signal (по аналогии с тем, что было с панелями раньше)
# TODO:


class Path3dWidget(QWidget):
    """
    Класс талбицы
    """
    def __init__(self, scanner: PScanner):
        super().__init__()
        self.scanner = scanner
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        group = QGroupBox(self)
        group_layout = QVBoxLayout(group)
        """
        может, проще сделать так, чем сигналы настраивать
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
        self.widget1 = Table1Widget(self.scanner)
        group_layout.addWidget(self.widget1)
        self.layout.addWidget(group)

# написиать функцию, меняющую split на step, и функцию, меняющую сами данные (relative) и функцию (set current pos)


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
            #self.headerDataChange  использовать в другой функции
        return True

    def setCoords(self, x: float = None, y: float = None, z: float = None, w: float = None):
        if x is not None:
            self._data[0][0] = x
        print(x)

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
    def __init__(self, scanner: PScanner):
        super().__init__()
        self.scanner = scanner
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
        self.vbox = QWidget()

        self.vboxlayout = QVBoxLayout(self.vbox)  # вертикальный слой, содержащий комбобокс и чекбокс

        self.hbox = QWidget()
        self.hboxlayout = QHBoxLayout(self.hbox)  # горизонтальный слой с кнопкой сет коорд и вертик слой

        self.group = QGroupBox()
        self.group_layout = QVBoxLayout(self.group)

        #self.set_button = QPushButton("Set current coordinates")
        self.set_button = StateDepPushButton(
            state=self.scanner.states.is_connected,
            text="Set current coordinates",
            parent=self
        )
        self.set_button.clicked.connect(self.setCoords)

        self.hboxlayout.addWidget(self.set_button)

        self.split_step_box = QComboBox()
        self.items = ["Step", "Split"]
        self.split_step_box.addItem("Step")
        self.split_step_box.addItem("Split")
        self.split_step_box.currentTextChanged.connect(self.set_splits)
        self.vboxlayout.addWidget(self.split_step_box)

        self.check_relative = QCheckBox("Relatives coordinates")
        self.vboxlayout.addWidget(self.check_relative)
        self.hboxlayout.addWidget(self.vbox)

        self.temp_button = QPushButton("Print test button")
        self.temp_button.clicked.connect(self.go_table)  # временная кнопка. Необходимо, чтобы go_table была доступна
                                                    # вне класса - в эксперименте.
        self.temp_button.setProperty('color', 'red')
        self.layout.addWidget(self.temp_button)
        self.group_layout.addWidget(self.hbox)

        self.control_keys_V = ["Begin coordinates", "End coordinates", "Step", "Order"]
        self.control_keys_H = ["x", "y", "z", "w"]

        # формирование таблицы, в которой задаются значения координат, скоростей и шага для трех осей
        self.tableWidget = MeshTable(self.control_keys_H, self.control_keys_V, self)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableWidget.setFixedHeight(200)
        self.group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(self.group)
        self.layout.addWidget(self.tableWidget)

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

    def set_splits(self, i: str):                                          # по координатам в соответствии с  порядком
        self.control_keys_V[2] = i
        self.tableWidget.setVerticalHeader(self.control_keys_V)
        print(i)

    def setCoords(self):
        pos = self.scanner.instrument.position()
        self.tableWidget.model().setCoords(x = pos.x)

@dataclass
class Path3d(PPath):
    widget: QWidget = None
    points: np.ndarray = np.array([])
    scanner: PScanner = None
    def __post_init__(self):
        self.widget = Path3dWidget(self.scanner)
