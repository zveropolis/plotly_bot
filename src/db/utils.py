import logging

from pandas import DataFrame
from sqlalchemy import insert, select, update

from db.database import async_engine
from db.models import UserActivity, UserData

logger = logging.getLogger()


async def select_user(user_id):
    query = select(UserData).where(UserData.telegram_id == user_id)

    async with async_engine.connect() as conn:
        res = await conn.execute(query)
        return DataFrame(data=res.mappings().all())


async def insert_user(user_id, user_name):
    user_data = dict(
        telegram_id=user_id,
        telegram_name=user_name,
        admin=False,
        active=UserActivity.inactive,
    )

    query = insert(UserData).values(user_data)

    async with async_engine.connect() as conn:
        await conn.execute(query)
        await conn.commit()


async def __update_user_activity(user_id, activity):
    query = update(UserData).values(active=activity).filter_by(telegram_id=user_id)

    async with async_engine.connect() as conn:
        await conn.execute(query)
        await conn.commit()


async def delete_user(user_id):
    await __update_user_activity(user_id, activity=UserActivity.deleted)


async def recover_user(user_id):
    await __update_user_activity(user_id, activity=UserActivity.inactive)
