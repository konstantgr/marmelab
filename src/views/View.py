from PyQt6.QtWidgets import QWidget
from ..project.Project import PBaseTypes, PScannerTypes, PAnalyzerTypes
from typing import Union


class BaseView(QWidget):
    def __init__(self, model: Union[PBaseTypes, PScannerTypes, PAnalyzerTypes], *args, **kwargs):
        super(BaseView, self).__init__(*args, **kwargs)
        self.model = model

    def widget_display_name(self) -> str:
        return self.model.name
