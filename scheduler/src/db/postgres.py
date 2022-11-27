from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from src.core.config import db_settings

DB_URI = 'postgresql+psycopg2://{}:{}@{}/{}'.format(db_settings.user, db_settings.password, db_settings.host, db_settings.db)
engine = create_engine(DB_URI)
session = Session(bind=engine)
