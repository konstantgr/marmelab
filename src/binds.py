from .ModelView import ModelViewFactory

from .project.PAnalyzers import ToyAnalyser
from .project.PScanners import ToyScanner
from .project.PPaths import ToyPath
from .project.PExperiments import ToyExperiment

from .views.toy import ToyView
from .Builder import AppBuilder, FactoryGroups

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




