from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_scoped_session
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from asyncio import current_task
from core.config import settings

engine = create_async_engine(settings.postgres.dsn)
Base = declarative_base()


async_db = async_scoped_session(
    session_factory=sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        class_=AsyncSession,
    ),
    scopefunc=current_task,
)
