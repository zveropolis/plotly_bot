import logging

from asyncpg.exceptions import UniqueViolationError
from redis.asyncio import ConnectionPool, Redis
from redis.asyncio.client import Pipeline
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from core.config import settings
from core.err import redis_exceptor
from core.exceptions import DatabaseError, UniquenessError

logger = logging.getLogger("sqlalchemy")
rlogger = logging.getLogger("redis")


async_engine = create_async_engine(
    url=settings.DATABASE_URL,
    echo=False,  # Логирование всех выполняемых операций
    pool_size=10,  # Максимальное количество подключений к базе
    max_overflow=20,  # Количество дополнительных подключений при переполнении
)
async_session_factory = async_sessionmaker(async_engine)

__pool = ConnectionPool.from_url(settings.CASHBASE_URL, decode_responses=True)
redis_engine = Redis.from_pool(__pool)


async def execute_query(query, echo=True):
    async with async_session_factory() as session:
        async with session.begin():
            try:
                if echo:
                    q = query.compile()
                    if q.params:
                        logger.info(f"{q}\nQuery PARAMS: {q.params}")
                    else:
                        logger.info(str(q))

                res = await session.execute(query)
                session.expunge_all()

                return res

            except (UniqueViolationError, IntegrityError):
                await session.rollback()
                logger.warning("Эта запись в базе уже существует")
                raise UniquenessError
            except Exception:
                await session.rollback()
                logger.exception("Ошибка при подключении к БД", exc_info=query.__dict__)
                raise DatabaseError


@redis_exceptor
async def execute_redis_query(pipeline: Pipeline):
    if pipeline.command_stack:
        rlogger.info(f"TRYING TO REDIS QUERY :: {pipeline.command_stack}")
        async with pipeline as pipe:
            result = await pipe.execute()
            rlogger.info("REDIS QUERY COMPLETED")
            return result
    return []


@redis_exceptor
async def iter_redis_keys(key_pattern):
    return redis_engine.scan_iter(key_pattern)
