from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from typing import AsyncGenerator
from core.config import settings

# Global variables for engine and session factory
engine = None
async_session_factory = None

def init_database():
    """Initialize database engine and session factory"""
    global engine, async_session_factory
    
    if engine is None:
        # Ensure we're using asyncpg driver
        database_url = settings.DATABASE_URL
        if not database_url.startswith("postgresql+asyncpg://"):
            if database_url.startswith("postgresql://"):
                database_url = database_url.replace("postgresql://", "postgresql+asyncpg://")
            else:
                raise ValueError("DATABASE_URL must be a PostgreSQL connection string")
        
        engine = create_async_engine(
            database_url,
            echo=settings.DEBUG,
            future=True,
            pool_pre_ping=True,
            pool_recycle=300,
            pool_size=settings.DATABASE_POOL_SIZE,
            max_overflow=settings.DATABASE_MAX_OVERFLOW
        )
        
        async_session_factory = async_sessionmaker(
            engine,
            class_=AsyncSession,
            expire_on_commit=False
        )

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    if async_session_factory is None:
        init_database()
        
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()

async def close_database():
    """Close database engine"""
    global engine
    if engine:
        await engine.dispose()