import logging

from asyncpg.exceptions import UniqueViolationError
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from core.config import settings
from core.exceptions import DatabaseError, UniquenessError

logger = logging.getLogger()

async_engine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=False,  # Логирование всех выполняемых операций
    pool_size=5,  # Максимальное количество подключений к базе
    max_overflow=10,  # Количество дополнительных подключений при переполнении
)


async def execute_query(query):
    try:
        async with async_engine.connect() as conn:
            res = await conn.execute(query)
            await conn.commit()
    except (UniqueViolationError, IntegrityError):
        logger.warning("Эта запись в базе уже существует")
        raise UniquenessError
    except Exception:
        logger.exception("Ошибка при подключении к БД", exc_info=query.__dict__)
        raise DatabaseError
    else:
        return res
