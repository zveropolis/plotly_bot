import asyncio
import logging
import logging.config
import os
import sys

sys.path.insert(1, os.path.dirname(sys.path[0]))


from core.config import Base
from db import models as _
from db.database import async_engine

logging.config.fileConfig("log.ini", disable_existing_loggers=False)
logger = logging.getLogger()


async def async_connect():
    async with async_engine.connect() as conn:
        async_engine.echo = False
        await conn.run_sync(Base.metadata.drop_all)
        async_engine.echo = True
        await conn.run_sync(Base.metadata.create_all)
        await conn.commit()


if __name__ == "__main__":
    asyncio.run(async_connect())
