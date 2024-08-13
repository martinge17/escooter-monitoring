from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import sys

# import tomllib
import logging

"""
# Load configuration from file
try:
    file = open("config.toml", "rb")
except Exception:
    logging.error("Can't open config file", exc_info=True)
    exit(1)
else:
    with file:
        config = tomllib.load(file)

template = "postgresql+psycopg://{user}:{password}@{hostname}:{port}/{dbname}"
connection_str = template.format(
    user=config["database"]["user"],
    password=config["database"]["password"],
    hostname=config["database"]["db_hostname"],
    port=config["database"]["db_port"],
    dbname=config["database"]["db_name"],
)
"""

connection_str = "postgresql+psycopg://api:changeme@localhost:5432/scooter_data"  # TODO: FOR DEV ONLY

SQLALCHEMY_DB_URL = connection_str

engine = create_engine(SQLALCHEMY_DB_URL)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
