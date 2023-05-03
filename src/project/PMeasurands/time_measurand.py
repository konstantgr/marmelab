from typing import Union, Tuple
import numpy as np
import logging
from datetime import datetime

from src.project.Project import ProjectType
from src.project.Project import PMeasurand

logger = logging.getLogger(__name__)


class TimeMeas(PMeasurand):
    type_name = 'Time'

    def __init__(
            self,
            name: str
    ):
        super(TimeMeas, self).__init__(name=name)
        self.t_format = "YYYY-MM-DD H:M:S"
        self._data: Union[dict[str: str], None] = None

    def measure(self) -> np.ndarray:
        if self.t_format is not None:
            now = datetime.today()
            if self.t_format == "YYYY-MM-DD H:M:S":
                time1 = now.strftime("%Y-%m-%d %H:%M:%S")
            elif self.t_format == "MM-DD H:M:S":
                time1 = now.strftime("%m-%d %H:%M:%S")
            elif self.t_format == "H:M:S":
                time1 = now.strftime("%H:%M:%S")
            elif self.t_format == "unix":
                time1 = now.timestamp()
            else:
                raise TypeError("Unknown format")
            self._data = dict(
                time1=str(time1)
            )
            logger.info("times have been measured")
            self.signals.measured.emit()
            return np.array([list(self._data.values())])
        else:
            raise TypeError("No time format selected")

    def pre_measure(self) -> None:
        pass

    def get_measure_names(self) -> Tuple[str]:
        return tuple(["time1"])

    def get_data(self) -> Union[None, np.ndarray]:
        if self._data is not None:
            return np.array(list(self._data.values()))
        else:
            return None

    def set_time_format(self, time_format):
        self.t_format = time_format

    @classmethod
    def reproduce(cls, name: str, project: ProjectType) -> 'TimeMeas':
        return cls(name=name)
