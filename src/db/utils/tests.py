import asyncio
import logging

from sqlalchemy import select

from db.database import execute_query, execute_redis_query, redis_engine
from db.models import Transactions, UserData, WgConfig

logger = logging.getLogger()


async def test_base():
    async def __test_base(base):
        query = select(base)
        await execute_query(query)

    return await asyncio.gather(
        *(__test_base(base) for base in (UserData, Transactions, WgConfig)),
        return_exceptions=True,
    )


async def test_redis_base():
    pipe = redis_engine.pipeline()
    query = pipe.ping()

    return await asyncio.gather(
        *(execute_redis_query(pipe, query),),
        return_exceptions=True,
    )
