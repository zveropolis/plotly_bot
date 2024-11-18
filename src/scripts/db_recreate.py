"""Пересоздание БД"""

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
    """Восстанавливает таблицы в PostgreSQL.

    Эта функция удаляет все существующие таблицы и создает новые на основе
    метаданных базы данных.

    Raises:
        Exception: Если возникла ошибка при выполнении операций с базой данных.
    """
    async with async_engine.connect() as conn:
        async_engine.echo = False
        await conn.run_sync(Base.metadata.drop_all)
        async_engine.echo = True
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()


async def clear_redis():
    """Очищает базу данных Redis.

    Эта функция очищает все данные из текущей базы данных Redis, используя
    конвейер для выполнения команды `flushdb`.

    Raises:
        Exception: Если возникла ошибка при выполнении команды Redis.
    """
    pipe = redis_engine.pipeline()
    pipe.flushdb()
    await execute_redis_query(pipe)


if __name__ == "__main__":

    async def start():
        """Запускает процесс восстановления таблиц и очистки Redis.

        Эта функция собирает задачи для восстановления таблиц в PostgreSQL и
        очистки базы данных Redis, обрабатывает возможные исключения и ведет журнал.

        Raises:
            Exception: Если возникла ошибка при подключении к БД.
        """
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
