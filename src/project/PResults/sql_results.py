import numpy as np

from typing import Tuple
from pathlib import Path
from ..Project import PResults
import sqlalchemy as db
from sqlalchemy.orm import Session

from db_structures import create_db, ResultsDb


class SQLResults(PResults):
    def __init__(self, results: np.ndarray, names: Tuple[str, ...], db_path, create_db_flag=False):
        super(SQLResults, self).__init__(results=results, names=names, db_path=db_path)
        self.results = results
        self.names = names
        self.db_path = db_path

        if create_db_flag:
            self.create_db()

        self.engine = db.create_engine(Path('sqlite://') / self.db_path)
        self.connection = None

    def create_db(self):
        create_db(self.db_path)

    def connect(self):
        self.connection = self.engine.connect()

    def disconnect(self):
        self.connection.close()
        self.connection = None

    def get_data(self) -> np.ndarray:
        """
        Возвращает все сохраненные данные
        """
        return self.results

    def get_data_names(self) -> Tuple[str, ...]:
        """
        Возвращает названия колонок данных
        """
        return self.names

    def append_data(self, data: np.ndarray):
        """
        Добавить новую строку в результаты
        """
        if not self.connection:
            self.connect()

        with Session(self.engine) as session:
            for result_array in data:
                results = ResultsDb(*result_array)
                session.add(results)
                session.commit()

    # def to_csv(self, filepath: Path):
    #     delimiter = ','
    #     np.savetxt(filepath, self.results, delimiter=delimiter, header=delimiter.join(self.names))
