from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine as _create_engine
from sqlalchemy.orm import declarative_base

Base = declarative_base()


def create_engine(url: str) -> "_create_engine":
    return _create_engine(url, echo=False, future=True, pool_pre_ping=True)


def create_session_factory(engine) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        engine,
        expire_on_commit=False,
        class_=AsyncSession,
    )
