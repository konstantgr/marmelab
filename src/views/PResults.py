from PyQt6.QtWidgets import QWidget, QGroupBox, QHBoxLayout, QVBoxLayout, QPushButton, QComboBox, QFileDialog
from .View import BaseView, QWidgetType
from PyQt6.QtCore import Qt
from ..project.PResults.toy_results import ToyResults


class ResultsView(BaseView[ToyResults]):
    def construct_widget(self) -> QWidgetType:
        widget = QWidget()
        widget.setLayout(QVBoxLayout())

        group = QGroupBox()
        widget.layout().addWidget(group)

        group_layout = QVBoxLayout(group)
        group.setLayout(group_layout)
        group_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        h_box = QWidget()
        hbox_layout = QVBoxLayout(h_box)
        res_csv_button = QPushButton('Download result to .csv')
        res_csv_button.clicked.connect(self.save_file_csv)

        res_matlab_button = QPushButton('Download result to .matlab')
        res_matlab_button.clicked.connect(self.save_file_matlab)

        hbox_layout.addWidget(res_csv_button)
        hbox_layout.addWidget(res_matlab_button)

        group_layout.addWidget(h_box)
        widget.hide()
        return widget

    def save_file_csv(self):
        new_path: QFileDialog = self.get_save_file_name_csv()
        self.model.to_csv(new_path[0])

    def get_save_file_name_csv(self):
        file_filter = 'Data File (*.csv );'
        response = QFileDialog.getSaveFileName(
            caption='Save file as...',
            directory=f'.\\{self.model.name}',
            filter=file_filter
        )
        return response

    def save_file_matlab(self):
        new_path: QFileDialog = self.get_save_file_name_matlab()
        self.model.to_mat(new_path[0])

    def get_save_file_name_matlab(self):
        file_filter = 'Data File (*.mat );'
        response = QFileDialog.getSaveFileName(
            caption='Save file as...',
            directory=f'.\\{self.model.name}',
            filter=file_filter
        )
        return response






class ToyScannerControl(ResultsView):
    def display_name(self) -> str:
        return 'Control'


class ToyScannerSettings(ResultsView):
    def display_name(self) -> str:
        return 'Settings'

