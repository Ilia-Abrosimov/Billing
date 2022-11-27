from sqlalchemy import MetaData, Table
from sqlalchemy.ext.declarative import declarative_base
from src.db.postgres import engine

Base = declarative_base()
metadata = MetaData()


class Payment(Base):
    __table__ = Table('payments', metadata, autoload=True, autoload_with=engine)


class Subscription(Base):
    __table__ = Table('subscriptions', metadata, autoload=True, autoload_with=engine)
