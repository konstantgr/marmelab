import numpy as np
import pandas as pd
import sqlalchemy as db

from typing import Tuple
from pathlib import Path
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy import text

from ..Project import PResults
from .db_structures import create_db, ResultsDb


class SQLResults(PResults):
    def __init__(self, name):
        super(SQLResults, self).__init__(name=name)
        self.results = None
        self.names = None
        self.db_path = Path("")

        self.engine = None
        self.connection = None
        self.session = None

    def set_engine(self):
        self.engine = db.create_engine(str(self.db_path))

    def set_db_path(self, db_path: Path):
        self.db_path = f'sqlite:///{db_path}'  # Path('sqlite://') / db_path

    def set_db(self, existing=False, force_create=False):
        if not existing or force_create:
            create_db(self.db_path, force_create)

        self.set_engine()

    def set_names(self, names: Tuple[str, ...]):
        self.names = names

    def set_results(self, results: np.ndarray):
        self.results = results

    def connect(self):
        self.connection = self.engine.connect()
        Session = sessionmaker()
        Session.configure(bind=self.engine)

        self.session = Session()
        # session.add(ed_user)

    def disconnect(self):
        self.connection.close()
        self.connection = None

    def get_data(self, pandas=True) -> np.ndarray:
        """
        Возвращает все сохраненные данные
        """
        if pandas:
            sql = "SELECT * FROM Results;"
            with self.engine.begin() as conn:
                return pd.read_sql_query(text(sql), con=conn).to_numpy()
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
        # trans = self.connection.begin()

        for result_array in data:
            d = dict(zip(self.names, result_array))
            results = ResultsDb(**d)
            self.session.add(results)
            self.session.commit()

    @classmethod
    def reproduce(cls, name: str, project) -> "SQLResults":
        return cls(name=name)
