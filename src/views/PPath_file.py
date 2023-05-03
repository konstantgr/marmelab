from PyQt6.QtWidgets import QWidget, QGroupBox, QHBoxLayout, QVBoxLayout, QPushButton, QComboBox, QFileDialog
from .View import BaseView, QWidgetType
from PyQt6.QtCore import Qt
from ..project.PPaths.file_Path3d import FilePathModel
import numpy as np
import os

"""
 в модель передавать только абсолютный путь, в модели реализовать логику распарсинга
"""


class FilePathView(BaseView[FilePathModel]):
    def construct_widget(self) -> QWidgetType:
        widget = QWidget()
        widget.setLayout(QVBoxLayout())

        group = QGroupBox()
        widget.layout().addWidget(group)

        group_layout = QVBoxLayout(group)
        group.setLayout(group_layout)
        group_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        h_box = QWidget()
        hbox_layout = QHBoxLayout(h_box)
        file_button = QPushButton('Upload path (.csv format)')
        file_button.clicked.connect(self.open_file)

        hbox_layout.addWidget(file_button)

        group_layout.addWidget(h_box)
        widget.hide()
        return widget

    def open_file(self):
        path: QFileDialog = self.get_open_file_name()
        try:
            os.path.exists(path[0])
        except FileNotFoundError:
            raise FileNotFoundError

        path_array = np.genfromtxt(path[0], delimiter=',', dtype=float)

        print(path_array, type(path_array))
        self.model.set_path(path_array)


    def get_open_file_name(self):
        file_filter = 'Data File (*.csv);'
        response = QFileDialog.getOpenFileName(
            caption='Open file...',
            directory=f'.\\{self.model.name}',
            filter=file_filter
        )
        return response