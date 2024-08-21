import asyncio
import logging

from pandas import DataFrame
from sqlalchemy import insert, select, update

from db.database import execute_query
from db.models import Transactions, UserActivity, UserData, WgConfig

logger = logging.getLogger()


async def test_base():
    async def __test_base(base):
        query = select(base)
        await execute_query(query)

    return await asyncio.gather(
        *(__test_base(base) for base in (UserData, Transactions, WgConfig)),
        return_exceptions=True,
    )


async def select_user(user_id):
    query = select(UserData).where(UserData.telegram_id == user_id)
    res = await execute_query(query)

    return DataFrame(data=res.mappings().all())


async def insert_user(user_id, user_name):
    user_data = dict(
        telegram_id=user_id,
        telegram_name=user_name,
        admin=False,
        active=UserActivity.inactive,
    )

    query = insert(UserData).values(user_data)

    return await execute_query(query)


async def __update_user_activity(user_id, activity):
    query = update(UserData).values(active=activity).filter_by(telegram_id=user_id)
    await execute_query(query)


async def delete_user(user_id):
    await __update_user_activity(user_id, activity=UserActivity.deleted)


async def recover_user(user_id):
    await __update_user_activity(user_id, activity=UserActivity.inactive)
