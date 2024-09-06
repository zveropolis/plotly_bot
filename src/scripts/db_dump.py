import asyncio
import logging
import logging.config
import os
import sys

sys.path.insert(1, os.path.dirname(sys.path[0]))


from db.utils import async_dump

logging.config.fileConfig("log.ini", disable_existing_loggers=False)
logger = logging.getLogger()


if __name__ == "__main__":
    asyncio.run(async_dump())
