from ..Project import PPath, PScanner
from PyQt6.QtWidgets import QWidget, QHeaderView, QHBoxLayout, QTableView, QVBoxLayout, QSizePolicy, QGroupBox, QComboBox
import numpy as np
from typing import List
from src.views.Widgets.SettingsTable import QSmartTableModel
from PyQt6.QtCore import Qt, QObject, QModelIndex
from PyQt6.QtGui import QColor
from typing import Any
from src.views.Widgets import StateDepPushButton, StateDepCheckBox
import re
from ...scanner import Position


# TODO: split -> step с изменением метода формирования массива точек, в которых проводятся измерения
# TODO: итого: 4 таблицы, которые надо связать QStacked Widget, signal (по аналогии с тем, что было с панелями раньше)
# TODO: во вкладке эксперимент добавить связь с таблицей и с функцией do_table в частности, реализовать временный вектор,
# TODO: хранящий реальные данные сканер


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
        self.widget1 = Table1Widget(self.scanner)
        group_layout.addWidget(self.widget1)
        self.layout.addWidget(group)

# написиать функцию, меняющую split на step, и функцию, меняющую сами данные (relative) и функцию (set current pos)


class MeshTableModel(QSmartTableModel):
    """
    класс, обеспечивающий проверку значений в таблице
    """
    def __init__(self, parent: QObject = None, ):
        super(QSmartTableModel, self).__init__()
        self.control_keys_V = ["Begin coordinates", "End coordinates", "Step", "Order"]
        self.control_keys_H = ["x", "y", "z", "w"]
        # self.variable = Variable(name="", default_value=0, type=float, description="")
        # self.variable = Variable(name="", default_value=0, type=float, unit=Length, description="")  реализовать валидацию
        self.headers = self.control_keys_H
        self.v_headers = self.control_keys_V
        self._data = [["" for _ in range(len(self.headers))] for _ in range(4)]  # добавить None в валидные значения
        self.pattern = re.compile(r"^\d+(?:\.\d+)?\s*(?:\[\s*[a-zA-Z]*\s*])?$")
        self.relative = False

    def set_relative(self, state: bool):
        self.relative = state

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
            # elif self._valid(self._data[row][column], self.variable):
                # return
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
            # self.headerDataChange  использовать в другой функции
        return True

    def params_to_linspace(self):
        lst_x = []
        lst_y = []
        lst_z = []
        lst_w = []
        order1 = []

        x, y, z, w = [], [], [], []

        for _ in range(4):
            order1.append((self.index(3, _).data()))

        order = [int(i) for i in order1 if i.isdigit()]
        print(order)
        #  реализация считывания данных в таблице

        for _ in range(3):
            lst_x.append(self.index(_, self.control_keys_H.index("x")).data())
            lst_y.append(self.index(_, self.control_keys_H.index("y")).data())
            lst_z.append(self.index(_, self.control_keys_H.index("z")).data())
            lst_w.append(self.index(_, self.control_keys_H.index("w")).data())

        lst_x = [float(i) for i in lst_x if i != ''] # реализовать проверку на пустые значения. Если их нет, ничего не делать
        lst_y = [float(i) for i in lst_y if i != '']
        lst_z = [float(i) for i in lst_z if i != '']
        lst_w = [float(i) for i in lst_w if i != '']

        x = self.mesh_maker(lst_x)
        y = self.mesh_maker(lst_y)
        z = self.mesh_maker(lst_z)
        w = self.mesh_maker(lst_w)

        return x, y, z, w, order

    def mesh_maker(self, lst: List):
        """
        функция, которая формирует набор значений, в которых будет производиться измерения
        она выдает либо с заданным шагом, либо с фиксированным количеством точек
        :param lst:
        :return:
        """

        if len(lst) != 0:
            if self.relative:
                lst[1] = lst[0] + lst[1]  # немного не то. Надо текущую координату брать
                #lst[0] = self.scanner.instrument.position().

            if self.control_keys_V[2] == "Step":
                arr = int(abs(lst[0] - lst[1] - 1) / lst[2])
                mesh = np.linspace(lst[0], lst[1], arr)
            elif self.control_keys_V[2] == "Split":
                mesh = np.linspace(lst[0], lst[1], int(lst[2]))
            return mesh
        else:
            pass


    def setCoords(self, x: float = None, y: float = None, z: float = None, w: float = None):
        if x is not None:
            self._data[0][0] = x
            index = self.index(0, 0)
            self.dataChanged.emit(index, index)
        if y is not None:
            self._data[0][1] = y
            index = self.index(0, 1)
            self.dataChanged.emit(index, index)
        if z is not None:
            self._data[0][2] = z
            index = self.index(0, 2)
            self.dataChanged.emit(index, index)
        if w is not None:
            self._data[0][3] = w
            index = self.index(0, 3)
            self.dataChanged.emit(index, index)


class MeshTable(QTableView):
    """
    Реализация умной таблицы
    """

    def __init__(self, parent: QWidget = None):
        super(MeshTable, self).__init__(parent)
        self.model = MeshTableModel(parent)
        self.setModel(self.model)
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

        self.set_button = StateDepPushButton(
            state=self.scanner.states.is_connected,
            text="Set current coordinates",
            parent=self
        )

        self.set_button.clicked.connect(self.set_coords)
        self.hboxlayout.addWidget(self.set_button)

        self.split_step_box = QComboBox()
        self.items = ["Step", "Split"]
        self.split_step_box.addItem("Step")
        self.split_step_box.addItem("Split")
        self.split_step_box.currentTextChanged.connect(self.set_splits)
        self.vboxlayout.addWidget(self.split_step_box)

        self.check_relative = StateDepCheckBox(
            state=self.scanner.states.is_connected,
            text="Relatives coordinates",
            parent=self
        )
        self.check_relative.stateChanged.connect(self.set_relate_coords)

        self.test_button = QPushButton("TEST BUTTON")  # временная тестовая кнопка
        self.test_button.setStyleSheet('QPushButton {background-color: #DAD8A3; color: black;}')
        self.test_button.clicked.connect(self.go_table)
        self.vboxlayout.addWidget(self.test_button)

        self.vboxlayout.addWidget(self.check_relative)
        self.hboxlayout.addWidget(self.vbox)
        self.group_layout.addWidget(self.hbox)

        # формирование таблицы, в которой задаются значения координат, скоростей и шага для трех осей
        self.tableWidget = MeshTable(self)
        self.tableWidget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tableWidget.setFixedHeight(200)
        self.group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

        self.layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.layout.addWidget(self.group)
        self.layout.addWidget(self.tableWidget)



    def go_table(self):
        """
        This function makes movement by coords from table
        """
        #  здесь вызов конвертации параметров из таблицы в списки

        keys_str = {
            1: self.tableWidget.model.control_keys_H[0],
            2: self.tableWidget.model.control_keys_H[1],
            3: self.tableWidget.model.control_keys_H[2],
            4: self.tableWidget.model.control_keys_H[3]
        }

        x, y, z, w, order = self.tableWidget.model.params_to_linspace()
        # эти словари нужны для выгрузки данных
        keys = {
            1: x,
            2: y,
            3: z,
            4: w,
        }
        #print(f"x={x}, y={y}, z={z}, w={w}")  # принт для проверки данных
        print([keys[i] for i in order], "".join([keys_str[i] for i in order]))

        #self.do_line([keys[i] for i in order], "".join([keys_str[i] for i in order]))   # вызов функции следования
        # по координатам в соответствии с  порядком

    # def do_line(self, coords: List[np.array], order: str, current_position: List = None):
    #     """
    #     настроить работу функции, которая перемещает сканнер по данным из таблицы. Я знаю, она должна быть в эксперименте
    #     :param coords:
    #     :param order:
    #     :param current_position:
    #     :return:
    #     """
    #     if current_position is None:
    #         current_position = []
    #     if len(coords) > 1:
    #         for coord in coords[0]:
    #             self.do_line(coords[1:], order, [*current_position, coord])
    #     else:
    #         for coord in coords[0]:
    #             temp_coord = [*current_position, coord]
    #             temp_doc = {order[i]: temp_coord[i] for i in range(len(order))}
    #             new_pos = self.scanner.instrument.position(**temp_doc)
    #             self.scanner.instrument.goto(new_pos)
    #             self.measurements()  # пока заглушка. надо сделать чтобы измеряла что-то в точке

    def set_splits(self, i: str):
        """
        функция меняет split на step и наоборот в таблице
        :param i:
        :return:
        """
        self.tableWidget.model.control_keys_V[2] = i
        self.tableWidget.model.headerDataChanged.emit(Qt.Orientation.Vertical, 0, 1)

    def set_coords(self):  #  перенести в модель
        pos = self.scanner.instrument.position()
        self.tableWidget.model.setCoords(x=pos.x, y=pos.y, z=pos.z, w=pos.w)
        # снимает галочку "относит. координаты". если используются текущ коорд.
        self.check_relative.setChecked(False)

    def set_relate_coords(self, state):
        """
        координаты становятся относительными. То есть текущая точка становится нулем. Однако реальные координаты надо
        все-таки где-mo сохранить
        :return:
        """

        if state:
            #  добавить сохранение данных
            self.tableWidget.model.setCoords(x=0, y=0, z=0, w=0)
        else:
            self.set_coords()
        self.tableWidget.model.set_relative(state)


class Path3d(PPath):
    def __init__(
            self,
            name: str,
            scanner: PScanner,
    ):
        super(Path3d, self).__init__(
            name=name,
            widget=Path3dWidget(scanner=scanner),
        )
        self.points: np.ndarray = np.array([[1000*i, 0, 0] for i in range(5)])

    def get_points(self) -> list[Position]:
        return [Position(1000*i, 0, 0) for i in range(5)]
