from sqlalchemy.ext.asyncio import async_sessionmaker, AsyncSession, create_async_engine

from database.models import Base


DB_LITE = "sqlite+aiosqlite:///my_base.db"

engine = create_async_engine(url=DB_LITE, echo=True)

session_maker = async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


async def create_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)