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
from db import models as _
from db.database import async_engine

logging.config.fileConfig("log.ini", disable_existing_loggers=False)
logging.getLogger("sqlalchemy.engine.Engine").setLevel(logging.INFO)
logger = logging.getLogger()


DUMPNAME = "regular_dump_06_11_2024-09_43.sql"
PLATFORM: Literal["Windows", "Linux"] = platform.system()


async def postgresql_recover_tables():
    async with async_engine.connect() as conn:
        async_engine.echo = False
        await conn.run_sync(Base.metadata.drop_all)
        async_engine.echo = True
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()

    cmd = (
        f"psql -U {settings.DB_USER} "
        f"-h {settings.DB_HOST} "
        f"-d {settings.DB_NAME} "
        f'-f {os.path.join(PATH, "src", "db", "dumps", DUMPNAME)}'
    )
    if PLATFORM == "Windows":
        cmd = f"$env:PGPASSWORD = {settings.DB_PASS.get_secret_value()}; " + cmd
        logger.error(
            "ЭТА ПЛАТФОРМА НЕ ПОДДЕРЖИВАЕТСЯ",
        )
        return

    elif PLATFORM == "Linux":
        cmd = f"export PGPASSWORD={settings.DB_PASS.get_secret_value()} && {cmd}"

    logger.info(f"Executing command: {cmd}")

    proc = await asyncio.create_subprocess_shell(
        cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
    )
    stdout, stderr = await proc.communicate()

    logger.info(f"pg_dump exited with {proc.returncode}")

    if proc.returncode != 0:
        error_message = stderr.decode("utf-8", errors="ignore")
        logger.error(f"Ошибка создания дампа БД: {error_message}")


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

    loop = asyncio.get_event_loop()
    loop.run_until_complete(start())
