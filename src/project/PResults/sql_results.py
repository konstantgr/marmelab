import numpy as np
import pandas as pd
import sqlalchemy as db

from typing import Tuple
from pathlib import Path
from sqlalchemy.orm import Session

from ..Project import PResults
from db_structures import create_db, ResultsDb


class SQLResults(PResults):
    def __init__(self, name):
        super(SQLResults, self).__init__(name=name)
        self.results = None
        self.names = None
        self.db_path = ''

        self.engine = db.create_engine(Path('sqlite://') / self.db_path)
        self.connection = None

    def set_db(self):
        self.create_db()

    def set_db_path(self, db_path: Path):
        self.db_path = db_path

    def set_names(self, names: Tuple[str, ...]):
        self.names = names

    def set_results(self, results: np.ndarray):
        self.results = results

    def create_db(self):
        create_db(self.db_path)

    def connect(self):
        self.connection = self.engine.connect()

    def disconnect(self):
        self.connection.close()
        self.connection = None

    def get_data(self, pandas=True) -> np.ndarray:
        """
        Возвращает все сохраненные данные
        """
        if pandas:
            sql = "SELECT * FROM Results"
            return pd.read_sql(sql, con=self.engine).to_numpy()
        else:
            return np.array(ResultsDb.query.all().fetchall())

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

    @classmethod
    def reproduce(cls, name: str, project) -> 'SQLResults':
        return cls(name=name)
