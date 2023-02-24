from .project import Project
from .project.Project import PBaseTypes, PStorage, PScannerTypes, PAnalyzerTypes

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
            connected_list: List = None
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
        if self.storage is not None:
            self.storage.delete(self.model)
        if self.connected_list is not None:
            self.connected_list.remove(self)
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
    ):
        """

        :param view_types: список классов вьюшек
        :param model_type: класс модели
        :param model: модель
        """
        self.view_types = view_types
        self.model_type: Type[PBaseTypes] = model_type
        self.model = model

        if self.model is None and self.model_type is None:
            raise ValueError("only one of model and model_type has to be None")
        if self.model is not None and self.model_type is not None:
            raise ValueError("model or model_type has to be None")

        self.type = self.model_type if self.model is None else type(self.model)
        self.connected_list = None

    def create(self, project: Project, from_model: PBaseTypes = None) -> ModelView:
        """Create ModelView instance and add its model to storage"""
        if from_model is not None:
            storage = None
            model = from_model
        elif self.model is None:
            model_type = self.model_type
            storage = project.get_storage_by_class(model_type)
            model_name = f'{model_type.base_name}+{storage.last_index+1}'
            model = self.model_type.reproduce(name=model_name, project=project)
            storage.append(model)
        else:
            storage = None
            model = self.model
        model_view = ModelView(
            model=model,
            views=tuple(view_cl(model) for view_cl in self.view_types),
            storage=storage,
            connected_list=self.connected_list
        )
        if self.connected_list is not None:
            self.connected_list.append(model_view)
        return model_view

    def connect_to_list(self, list_: List[ModelView]):
        """Connects factory to the list. Factory will add a new ModelViews to it"""
        self.connected_list = list_
