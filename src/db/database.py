import logging

from asyncpg.exceptions import UniqueViolationError
from redis import exceptions as rexc
from redis.asyncio import ConnectionPool, Redis
from redis.asyncio.client import Pipeline
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import create_async_engine

from core.config import settings
from core.exceptions import DatabaseError, UniquenessError

logger = logging.getLogger()

async_engine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=False,  # Логирование всех выполняемых операций
    pool_size=5,  # Максимальное количество подключений к базе
    max_overflow=10,  # Количество дополнительных подключений при переполнении
)
__pool = ConnectionPool.from_url(settings.CASHBASE_URL, decode_responses=True)
redis_engine = Redis.from_pool(__pool)


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


async def execute_redis_query(pipeline: Pipeline):
    try:
        logquery = str(pipeline.command_stack)#.strip("[](){},")
        logger.info(f"TRYING TO REDIS QUERY :: {logquery}")
        async with pipeline as pipe:
            result = await pipe.execute()
            logger.info("REDIS QUERY COMPLETED")
            return result

    except rexc.AuthenticationError:
        logger.exception(f"Ошибка аутентификации при подключении к Redis :: {logquery}")
        raise DatabaseError
    except rexc.ConnectionError:
        logger.exception(f"Ошибка подключения к Redis :: {logquery}")
        raise DatabaseError
    except rexc.TimeoutError:
        logger.exception(f"Превышено время ожидания при работе с Redis :: {logquery}")
        raise DatabaseError
    except IndexError:
        logger.exception("Command Stack is empty")
        raise DatabaseError
    except rexc.RedisError:
        logger.exception(f"Произошла неизвестная ошибка c Redis :: {logquery}")
        raise DatabaseError
