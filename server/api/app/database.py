from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from functools import lru_cache

from config import Settings, Database


@lru_cache
def get_db_settings():
    return Settings().database


def connection_str(db_settings: Database):

    template = "postgresql+psycopg://{user}:{password}@{hostname}:{port}/{dbname}"
    connection_str = template.format(
        user=db_settings.user,
        password=db_settings.password,
        hostname=db_settings.db_hostname,
        port=db_settings.db_port,
        dbname=db_settings.db_name,
    )
    return connection_str


engine = create_engine(connection_str(get_db_settings()))

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
