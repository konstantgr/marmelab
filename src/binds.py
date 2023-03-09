from .ModelView import ModelViewFactory

from .project.PPaths import ToyPath
from .project.PExperiments import ToyExperiment
from .project.PPlots import PRTPlot1D
from .project.Project import PPlot1D, PPlot2D    # TODO: убрать

from .views.toy import ToyView
from .views.PPlots import RTPlot1DView
from .builder import AppBuilder, FactoryGroups
from . import icons

AppBuilder.register_factory(
    ModelViewFactory(
        view_types=(ToyView,),
        model_type=ToyPath,
        icon=icons.path_table
    ),
    group=FactoryGroups.paths
)

AppBuilder.register_factory(
    ModelViewFactory(
        view_types=(ToyView,),
        model_type=ToyPath,
        icon=icons.path_file
    ),
    group=FactoryGroups.paths
)

AppBuilder.register_factory(
    ModelViewFactory(
        view_types=(RTPlot1DView,),
        model_type=PRTPlot1D,
        icon=icons.plot1d
    ),
    group=FactoryGroups.rtplots
)

AppBuilder.register_factory(
    ModelViewFactory(
        view_types=(ToyView,),
        model_type=PPlot2D,
        icon=icons.plot2d
    ),
    group=FactoryGroups.rtplots
)


AppBuilder.register_factory(
    ModelViewFactory(
        view_types=(ToyView,),
        model_type=ToyExperiment,
        icon=icons.experiment_icon
    ),
    group=FactoryGroups.experiments
)

AppBuilder.register_factory(
    ModelViewFactory(
        view_types=(ToyView,),
        model_type=PPlot1D,
        icon=icons.plot1d
    ),
    group=FactoryGroups.resplots
)

AppBuilder.register_factory(
    ModelViewFactory(
        view_types=(ToyView,),
        model_type=PPlot2D,
        icon=icons.plot2d
    ),
    group=FactoryGroups.resplots
)



