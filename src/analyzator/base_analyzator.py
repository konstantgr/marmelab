import abc
from typing import List
from src.analyzator.analyzator_parameters import SParameters, FrequencyParameters, AnalyzatorType, ResultsFormatType
from src import EmptySignal


class AnalyzatorConnectionError(Exception):
    def __init__(self):
        super().__init__("Error in analyzator connection")


class AnalyzerSignals(metaclass=abc.ABCMeta):
    """
    Базовые сигналы анализатора
    """

    @property
    @abc.abstractmethod
    def data(self) -> EmptySignal:
        """
        Сигнал с данными анализатора
        """

    @property
    @abc.abstractmethod
    def is_connected(self) -> EmptySignal:
        """
        Сигнал с состоянием анализатора
        """


class BaseAnalyzator(abc.ABC):
    @property
    @abc.abstractmethod
    def analyzator_type(self) -> AnalyzatorType:
        raise NotImplementedError('analyzator_type property not implemented yet')

    @abc.abstractmethod
    def connect(self) -> bool:
        raise NotImplementedError('connect method not implemented yet')

    @abc.abstractmethod
    def disconnect(self) -> bool:
        raise NotImplementedError('disconnect method not implemented yet')

    @abc.abstractmethod
    def get_scattering_parameters(
            self,
            parameters: List[SParameters],
            frequency_parameters: FrequencyParameters,
            results_formats: List[ResultsFormatType]
    ) -> dict[str: List[float]]:
        raise NotImplementedError('get_scattering_parameters method not implemented yet')

    @abc.abstractmethod
    def __enter__(self):
        raise NotImplementedError('__enter__ method not implemented yet')

    @abc.abstractmethod
    def __exit__(self, type, value, traceback):
        raise NotImplementedError('__exit__ method not implemented yet')
