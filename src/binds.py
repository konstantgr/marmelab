from .ModelView import ModelViewFactory

from .project.PPaths import ToyPath
from .project.PExperiments import ToyExperiment

from .views.toy import ToyView
from .builder import AppBuilder, FactoryGroups
from . import icons

AppBuilder.register_factory(
    ModelViewFactory(
        view_types=(ToyView,),
        model_type=ToyPath,
        icon=icons.path_icon
    ),
    group=FactoryGroups.paths
)

AppBuilder.register_factory(
    ModelViewFactory(
        view_types=(ToyView,),
        model_type=ToyExperiment,
        icon=icons.experiment_icon
    ),
    group=FactoryGroups.experiments
)




