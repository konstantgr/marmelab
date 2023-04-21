import os.path

from PyQt6.QtWidgets import QWidget, QGroupBox, QHBoxLayout, QVBoxLayout, QPushButton, QComboBox, QFileDialog
from .View import BaseView, QWidgetType
from PyQt6.QtCore import Qt
import shutil
from os import path


class ToyView(BaseView):
    def construct_widget(self) -> QWidgetType:
        group = QGroupBox()
        group_layout = QVBoxLayout(group)

        group.setLayout(group_layout)
        group_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        h_box = QWidget()
        hbox_layout = QHBoxLayout(h_box)
        res_button = QPushButton('Download result')
        res_button.clicked.connect(self.save_file)

        self.res_box = QComboBox()
        self.items = self.fined_csv_files()
        self.res_box.addItems(self.items)

        hbox_layout.addWidget(res_button)
        hbox_layout.addWidget(self.res_box)

        group_layout.addWidget(h_box)
        return group

    def save_file(self):
        new_path: QFileDialog = self.get_save_file_name()
        print(new_path)
        try:
            file_path = os.path.abspath(self.res_box.currentText())
        except Exception as e:
            raise e
        shutil.move(file_path, new_path[0])

    def fined_csv_files(self):
        all_files = []
        for root, dirs, files in os.walk('pyqt_app'):
            for file in files:
                print(file)
                if file.endswith(".csv"):
                    path_file = os.path.join(root, file)
                    all_files.append(path_file)

        return all_files


    def get_save_file_name(self):
        file_filter = 'Data File (*.csv );'
        response = QFileDialog.getSaveFileName(
            caption='Save file as...',
            directory=r'\pyqt_app\meas1_2023-04-21',
            filter=file_filter
        )

        return response


class ToyScannerControl(ToyView):
    def display_name(self) -> str:
        return 'Control'


class ToyScannerSettings(ToyView):
    def display_name(self) -> str:
        return 'Settings'

