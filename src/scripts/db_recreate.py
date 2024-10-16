import asyncio
import logging
import logging.config
import os
import sys

sys.path.insert(1, os.path.dirname(sys.path[0]))


from core.config import Base
from db import models as _
from db.database import async_engine, execute_redis_query, redis_engine

logging.config.fileConfig("log.ini", disable_existing_loggers=False)
logging.getLogger("sqlalchemy.engine.Engine").setLevel(logging.INFO)
logger = logging.getLogger()


async def postgresql_recreate_tables():
    async with async_engine.connect() as conn:
        async_engine.echo = False
        await conn.run_sync(Base.metadata.drop_all)
        async_engine.echo = True
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()


async def clear_redis():
    pipe = redis_engine.pipeline()
    pipe.flushdb()
    await execute_redis_query(pipe)


if __name__ == "__main__":

    async def start():
        bases = await asyncio.gather(
            *(postgresql_recreate_tables(), clear_redis()),
            return_exceptions=True,
        )

        for base in bases:
            try:
                if isinstance(base, Exception):
                    raise base
            except Exception:
                logger.exception("Возникло исключение при подключении к БД")
                raise

    loop = asyncio.get_event_loop()
    loop.run_until_complete(start())
