from ..project.PPaths import TablePathModel
from .description import path_description
from .View import BaseView, QWidgetType
from PyQt6.QtWidgets import QWidget, QHeaderView, QHBoxLayout, QTableView, QVBoxLayout, QSizePolicy, QGroupBox, \
    QComboBox, QPushButton, QWidgetAction, QTextBrowser, QLabel
from src.views.Widgets import StateDepPushButton, StateDepCheckBox
from PyQt6.QtCore import Qt
from PyQt6 import QtGui


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
        items = ["Points", "Step"]
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

        hbox_layout.addWidget(vbox)  # добавление вертикального виджета (содежит комбо и чек боксы) в гориз. слой
        group_layout.addWidget(hbox)  # создание отдельной группы для горизонтального слоя (отображение в рамке)
        layout.addWidget(group)

        # move_down = QWidgetAction(QtGui.QAction.)

        table_widget = QTableView()
        table_widget.setModel(self.model.table_model)

        # table_widget.addAction(move_down)
        table_widget.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table_widget.verticalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        table_widget.setFixedHeight(200)
        group.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Maximum)

        layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        layout.addWidget(table_widget)

        description_text = QLabel()
        description_text.setAlignment(Qt.AlignmentFlag.AlignTop)
        description_text.setText(path_description)

        layout.addWidget(description_text)
        return widget

    def set_split_type(self, split_type: str):
        self.model.set_split_type(split_type.lower())

    def set_trajectory_type(self, trajectory_type: str):
        self.model.set_trajectory_type(trajectory_type)
