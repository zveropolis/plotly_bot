import asyncio
import logging
import logging.config
import os
import platform
import sys
from typing import Literal

sys.path.insert(1, os.path.dirname(sys.path[0]))


from core.config import Base, settings
from core.path import PATH
from db import models as _  # COMMENT TRIGGER
from db.database import async_engine

logging.config.fileConfig("log.ini", disable_existing_loggers=False)
logging.getLogger("sqlalchemy.engine.Engine").setLevel(logging.INFO)
logger = logging.getLogger()


DUMPNAME = "dump_12_11_2024-16_20.sql"
PLATFORM: Literal["Windows", "Linux"] = platform.system()


async def postgresql_recover_tables():
    terminate = (
        f"psql -U {settings.DB_USER} "
        f"-h {settings.DB_HOST} "
        "-d nullbase "
        f"-c \"SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '{settings.DB_NAME}';\""
    )
    drop = (
        f"psql -U {settings.DB_USER} "
        f"-h {settings.DB_HOST} "
        "-d nullbase "
        f'-c "DROP DATABASE IF EXISTS {settings.DB_NAME};"'
    )

    create = (
        f"psql -U {settings.DB_USER} "
        f"-h {settings.DB_HOST} "
        "-d nullbase "
        f"""-c \"CREATE DATABASE {settings.DB_NAME}
                    WITH
                    OWNER = {settings.DB_USER}
                    ENCODING = 'UTF8'
                    LC_COLLATE = 'en_US.utf8'
                    LC_CTYPE = 'en_US.utf8'
                    TABLESPACE = pg_default
                    CONNECTION LIMIT = -1
                    IS_TEMPLATE = False;\"
                        """
    )

    recover = (
        f"psql -U {settings.DB_USER} "
        f"-h {settings.DB_HOST} "
        f"-d {settings.DB_NAME} "
        f'-f {os.path.join(PATH, "src", "db", "dumps", DUMPNAME)}'
    )
    if PLATFORM == "Windows":
        # cmd = f"$env:PGPASSWORD = {settings.DB_PASS.get_secret_value()}; " + recover
        logger.error(
            "ЭТА ПЛАТФОРМА НЕ ПОДДЕРЖИВАЕТСЯ",
        )
        return

    elif PLATFORM == "Linux":
        login = f"export PGPASSWORD={settings.DB_PASS.get_secret_value()}"

    for cmd in (terminate, drop, create, recover):
        cmd = f"{login} && {cmd}"

        logger.info(f"Executing command: {cmd}")

        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )
        stdout, stderr = await proc.communicate()

        logger.info(f"pg_dump exited with {proc.returncode}")

        if proc.returncode != 0:
            error_message = stderr.decode("utf-8", errors="ignore")
            logger.error(f"Ошибка создания дампа БД: {error_message}")

        else:
            print(stdout.decode("utf-8", errors="ignore"))


async def create_new_tables():
    async with async_engine.connect() as conn:
        async_engine.echo = True
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()


if __name__ == "__main__":

    async def start():
        bases = await asyncio.gather(
            *(postgresql_recover_tables(),),
            return_exceptions=True,
        )

        for base in bases:
            try:
                if isinstance(base, Exception):
                    raise base
            except Exception:
                logger.exception("Возникло исключение при подключении к БД")
                raise

        await create_new_tables()

    loop = asyncio.get_event_loop()
    loop.run_until_complete(start())
