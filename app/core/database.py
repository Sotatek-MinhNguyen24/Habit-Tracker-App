from typing import AsyncGenerator, Annotated

from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncEngine,AsyncSession,create_async_engine

from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import DATABASE_URL

engine: AsyncEngine = create_async_engine(DATABASE_URL, echo=False, pool_pre_ping=True)

AsyncSessionLocal = sessionmaker(bind=engine,class_=AsyncSession, expire_on_commit=False,autoflush=False,future=True)

Base = declarative_base()

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

db_dependency = Annotated[AsyncSession, Depends(get_db)]