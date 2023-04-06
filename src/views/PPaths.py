from ..project.PPaths import TablePathModel
from .View import BaseView, QWidgetType
from PyQt6.QtWidgets import QWidget, QHeaderView, QHBoxLayout, QTableView, QVBoxLayout, QSizePolicy, QGroupBox, \
    QComboBox, QPushButton
from src.views.Widgets import StateDepPushButton, StateDepCheckBox
from PyQt6.QtCore import Qt


class TablePathView(BaseView[TablePathModel]):
    def __init__(self, *args, **kwargs):
        super(TablePathView, self).__init__(*args, **kwargs)
        self.states = self.model.scanner.states

    def construct_widget(self) -> QWidgetType:
        widget = QWidget()
        layout = QVBoxLayout()
        widget.setLayout(layout)

        vbox = QWidget()
        vbox_layout = QVBoxLayout(vbox)  # вертикальный слой, содержащий комбобокс и чекбокс

        hbox = QWidget()
        hbox_layout = QHBoxLayout(hbox)  # горизонтальный слой с кнопкой сет коорд и вертик слой

        group = QGroupBox()
        group_layout = QVBoxLayout(group)

        set_button = StateDepPushButton(
            state=self.states.is_connected,
            text="Set current coordinates",
            parent=widget
        )
        set_button.clicked.connect(self.model.set_current_coords)  # написать функцию
        hbox_layout.addWidget(set_button)

        step_split_box = QComboBox()
        items = ["Step", "Points"]
        step_split_box.addItem(items[0])
        step_split_box.addItem(items[1])
        step_split_box.currentTextChanged.connect(self.set_split_type)
        vbox_layout.addWidget(step_split_box)

        self.snake_lines_box = QComboBox()
        items_ = ["Snake", "Lines"]
        self.snake_lines_box.addItem(items_[0])
        self.snake_lines_box.addItem(items_[1])
        self.snake_lines_box.currentTextChanged.connect(self.set_trajectory_type)
        vbox_layout.addWidget(self.snake_lines_box)

        check_relative = StateDepCheckBox(
            state=self.states.is_connected,
            text="Relatives coordinates",
            parent=widget
        )
        check_relative.stateChanged.connect(self.model.set_relative)
        vbox_layout.addWidget(check_relative)

        # print_tr_button = StateDepPushButton(
        #     state=self.states.is_connected,
        #     text="Print the trajectory",
        #     parent=widget
        # )
        # print_tr_button.clicked.connect(self.model.get_path) # должна вызываться ф-ия mesh_maker
        # vbox_layout.addWidget(print_tr_button)  #  тестовая кнопка, принтующая точки в консоль

        hbox_layout.addWidget(vbox)  # добавление вертикального виджета (содежит комбо и чек боксы) в гориз. слой
        group_layout.addWidget(hbox)  # создание отдельной группы для горизонтального слоя (отображение в рамке)
        layout.addWidget(group)

        table_widget = QTableView()
        table_widget.setModel(self.model.table_model)
        table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table_widget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table_widget.setFixedHeight(200)
        group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(table_widget)
        return widget

    def set_split_type(self, split_type: str):
        self.model.set_split_type(split_type.lower())

    def set_trajectory_type(self, trajectory_type: str):
        self.model.set_trajectory_type(trajectory_type)
