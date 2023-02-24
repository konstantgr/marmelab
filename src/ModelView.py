from .project import Project
from .project.Project import PBaseTypes, PStorage, PScannerTypes, PAnalyzerTypes
from PyQt6.QtGui import QIcon
from .icons import base_icon
from .views.View import BaseView
from typing import Union, Type, List, Tuple, Any, Dict

ModelView_ViewTreeType = Tuple[str, Union[None, BaseView, List[Tuple[str, BaseView]]]]


class ModelView:
    """Класс, который хранит вьюшку и ее модель"""
    def __init__(
            self,
            model: PBaseTypes,
            views: Tuple[BaseView],
            storage: PStorage = None,
            connected_list: List = None,
            icon: QIcon = None,
            removable: bool = True,
    ):
        """

        :param model: модель
        :param views: вью
        :param storage: хранилище, где хранится модель
        """
        self.model = model
        self.views = views
        self.storage = storage
        self.connected_list = connected_list
        self.icon = icon
        self.removable = removable

    def view_tree(self) -> ModelView_ViewTreeType:
        """Create list which represents tree structure"""
        if len(self.views) == 0:
            return self.model.name, None
        elif len(self.views) == 1:
            return self.model.name, self.views[0]
        else:
            return self.model.name, [(view.display_name(), view) for view in self.views]

    def delete(self):
        """Delete an instance from storage and del itself"""
        if self.connected_list is not None:
            self.connected_list.remove(self)
        if self.storage is not None:
            self.storage.delete(self.model)
        for view in self.views:
            view.widget.deleteLater()
        # TODO: проверить, что все удаляется
        del self.views
        del self.model


class ModelViewFactory:
    """Фабрика экземпляров ModelView"""
    def __init__(
            self,
            view_types: Tuple[Type[BaseView], ...],
            model_type: Type[PBaseTypes] = None,
            model: Union[PBaseTypes, PAnalyzerTypes, PScannerTypes] = None,
            icon: QIcon = base_icon,
            reproducible: bool = True,
            removable: bool = True,
    ):
        """

        :param view_types: список классов вьюшек
        :param model_type: класс модели
        :param model: модель
        :param icon: иконка
        :param reproducible: может ли сфабрикован ModelView пользователем
        :param removable: может ли ModelView быть удален пользователем
        """
        self.view_types = view_types
        self.model_type: Type[PBaseTypes] = model_type
        self.model: Union[PBaseTypes, PAnalyzerTypes, PScannerTypes] = model
        self.icon = icon
        self.reproducible = reproducible
        self.removable = removable

        if self.model is None and self.model_type is None:
            raise ValueError("only one of model and model_type has to be None")
        if self.model is not None and self.model_type is not None:
            raise ValueError("model or model_type has to be None")

        if self.model_type is not None:
            self.type: Union[PBaseTypes, PScannerTypes, PAnalyzerTypes] = self.model_type
        else:
            self.type: Union[PBaseTypes, PScannerTypes, PAnalyzerTypes] = type(self.model)
        self.connected_list = None

    def create(self, project: Project, from_model: PBaseTypes = None) -> ModelView:
        """Create ModelView instance and add its model to storage"""
        if from_model is not None:
            storage = project.get_storage_by_class(type(from_model))
            model = from_model
        elif self.model is None:
            model_type = self.model_type
            storage = project.get_storage_by_class(model_type)
            model_name = f'{model_type.base_name}{storage.last_index+1}'
            model = self.model_type.reproduce(name=model_name, project=project)
        else:
            storage = None
            model = self.model

        views = []
        for view_cl in self.view_types:
            view = view_cl(model)
            view.construct()
            views.append(view)

        model_view = ModelView(
            model=model,
            views=tuple(views),
            storage=storage,
            connected_list=self.connected_list,
            icon=self.icon,
            removable=self.removable
        )
        if self.connected_list is not None:
            self.connected_list.append(model_view)
        if storage is not None and model not in storage.data:
            storage.append(model)
        return model_view

    def connect_to_list(self, list_: List[ModelView]):
        """Connects factory to the list. Factory will add a new ModelViews to it"""
        self.connected_list = list_
