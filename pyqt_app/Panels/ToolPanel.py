from src.project.Widgets import StateDepPushButton
from PyQt6.QtWidgets import QToolBar, QPushButton
from pyqt_app import project
import logging
from pyqt_app.app_project import paths, objects
from src.project.PPaths import Path3d
from src.project.PObjects import Object3d
import numpy as np
logger = logging.getLogger()


class ToolPanel(QToolBar):
    def __init__(self, *args, **kwargs):
        super(QToolBar, self).__init__(*args, **kwargs)
        self.path_counter = 1
        self.obj_counter = 1
        self.upd_button = QPushButton("Update current position")
        self.add_path_button = QPushButton("Add path")
        self.add_obj_button = QPushButton("Add object")
        self.abort_button = StateDepPushButton(
            state=project.scanner.states.is_connected,
            text="Abort",
            parent=self
        )
        self.abort_button.setProperty('color', 'red')

        self.addWidget(self.upd_button)
        self.addWidget(self.add_path_button)
        self.addWidget(self.add_obj_button)
        self.addWidget(self.abort_button)

        self.add_obj_button.clicked.connect(self.obj_adder)
        self.add_path_button.clicked.connect(self.path_adder)
        self.upd_button.clicked.connect(self.upd_cur_pos)
        self.abort_button.clicked.connect(project.scanner.instrument.abort)

    @staticmethod
    def upd_cur_pos():
        project.scanner.instrument.position()

    def path_adder(self):
        self.path_counter += 1
        paths.append(
            Path3d(
                name=f'Path {self.path_counter}',
                points=np.array([[1000 * i, 0, 0] for i in range(5)]),
                scanner=project.scanner
            )
        )

    def obj_adder(self):
        self.obj_counter += 1
        objects.append(
            Object3d(
                name=f'Object {self.obj_counter}'
            )
        )

