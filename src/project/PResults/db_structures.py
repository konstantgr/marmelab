from sqlalchemy import Column, String, Integer, Float, Text, Boolean, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy_utils import database_exists, create_database
from pathlib import Path

base = declarative_base()


class ResultsDb(base):
    __tablename__ = 'Results'
    id = Column(Integer, primary_key=True)
    frequency = Column(Float)
    x = Column(Float)
    y = Column(Float)
    z = Column(Float)
    w = Column(Float)


def create_db(db_path: Path):
    engine = create_engine(str(db_path), echo=False)
    if not database_exists(engine.url):
        create_database(engine.url)

    base.metadata.drop_all(engine)
    base.metadata.create_all(engine)