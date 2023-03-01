from ..project.PPaths import TablePathModel
from .View import BaseView, QWidgetType
from PyQt6.QtWidgets import QPushButton

class TablePathView(BaseView[TablePathModel]):
    def __init__(self, *args, **kwargs):
        super(TablePathView, self).__init__(*args, **kwargs)

    def construct_widget(self) -> QWidgetType:
        widget = QPushButton("dsfa")
        return widget