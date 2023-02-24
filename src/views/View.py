from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QIcon
from ..project.Project import PBaseTypes, PScannerTypes, PAnalyzerTypes
from typing import Union
from ..icons import base_icon
from dataclasses import dataclass
from typing import List


class BaseView(QWidget):
    def __init__(self, model: Union[PBaseTypes, PScannerTypes, PAnalyzerTypes], *args, **kwargs):
        super(BaseView, self).__init__(*args, **kwargs)
        self.model = model

    def display_name(self) -> str:
        return self.model.name

    def display_icon(self) -> QIcon:
        return base_icon
