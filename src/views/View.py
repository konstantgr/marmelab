from PyQt6.QtWidgets import QWidget
from PyQt6.QtGui import QIcon
from ..project.Project import PBaseTypes, PScannerTypes, PAnalyzerTypes
from typing import Union, Type, Generic, TypeVar
from ..icons import base_icon
from abc import ABCMeta, abstractmethod

QWidgetType = TypeVar("QWidgetType", bound=QWidget)
# ModelType = Union[PBaseTypes, PScannerTypes, PAnalyzerTypes]
ModelType = TypeVar("ModelType")


class BaseView(Generic[ModelType], metaclass=ABCMeta):
    """Класс вьюшки"""
    def __init__(
            self,
            model: ModelType
    ):
        self.model = model
        self._widget: QWidgetType = None

    @property
    def widget(self) -> QWidgetType:
        """Виджет вьюшки"""
        if self._widget is None:
            raise RuntimeError("Widget was never constructed")
        return self._widget

    @abstractmethod
    def construct_widget(self) -> QWidgetType:
        """Вернуть виджет, который выполняет роль вьюшки"""

    def construct(self):
        """Создать виджет и привязать его к аттрибуту _widget"""
        if self._widget is not None:
            raise RuntimeError("Widget was already constructed")
        self._widget = self.construct_widget()

    def display_name(self) -> str:
        """Отражаемое в дереве имя вьюшки"""
        return self.model.name

    def display_icon(self) -> QIcon:
        """Отражаемая в дереве иконка вьюшки"""
        return base_icon
