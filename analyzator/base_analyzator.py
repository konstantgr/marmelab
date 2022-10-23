import abc
from dataclasses import dataclass
from typing import List
from analyzator_parameters import SParameters, FrequencyParameters


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
            parameter: List[SParameters.type],
            frequency_parameters: FrequencyParameters,
            results_formats: List[ResultsFormatType]
    ) -> List[float]:
        raise NotImplementedError('get_scattering_parameters method not implemented yet')

    @abc.abstractmethod
    def __enter__(self):
        raise NotImplementedError('__enter__ method not implemented yet')

    @abc.abstractmethod
    def __exit__(self, type, value, traceback):
        raise NotImplementedError('__exit__ method not implemented yet')
