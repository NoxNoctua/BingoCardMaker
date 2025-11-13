import os

from sqlalchemy import create_engine, MetaData
from sqlalchemy.orm import declarative_base, sessionmaker, DeclarativeBase

SQLALCHEMY_DATABASE_URL = "sqlite:///" + os.path.abspath(
	"./resources/bingo_database.sqlite"
)
print(SQLALCHEMY_DATABASE_URL)

engine = create_engine(SQLALCHEMY_DATABASE_URL, echo=False)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
	pass

metadata = MetaData()
metadata.reflect(bind=engine)


class EntityManager:
	def __init__(self, engine, SessionLocal, Base, metadata):
		self.engine = engine
		self.SessionLocal = SessionLocal
		self.Base = Base
		self.metadata = metadata


entity_manager = EntityManager(engine, SessionLocal, Base, metadata)