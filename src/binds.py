from .ModelView import ModelViewFactory

from .project.PPaths import ToyPath
from .project.PExperiments import ToyExperiment

from .views.toy import ToyView
from .builder import AppBuilder, FactoryGroups

AppBuilder.register_factory(
    ModelViewFactory(
        view_types=(ToyView,),
        model_type=ToyPath,
    ),
    group=FactoryGroups.paths
)

AppBuilder.register_factory(
    ModelViewFactory(
        view_types=(ToyView,),
        model_type=ToyExperiment,
    ),
    group=FactoryGroups.experiments
)




