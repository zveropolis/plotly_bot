import logging

from pandas import DataFrame
from sqlalchemy import insert, select, update

from db.database import execute_query
from db.models import UserActivity, UserData
from db.utils import CashManager

logger = logging.getLogger()


async def get_user(user_id):
    result = await CashManager(UserData).get(user_id, dict())

    if not result.empty:
        return result

    query = select(UserData).where(UserData.telegram_id == user_id)

    result = (await execute_query(query)).mappings().all()

    await CashManager(UserData).add(dict(*result), user_id)
    return DataFrame(result)


async def get_all_users(my_id):
    query = select(UserData).where(UserData.telegram_id != my_id)

    result = (await execute_query(query)).mappings().all()

    return DataFrame(result)


async def add_user(user_id, user_name):
    user_data = dict(
        telegram_id=user_id,
        telegram_name=user_name,
        admin=False,
        active=UserActivity.inactive,
        stage=1,
        month=0,
    )
    await CashManager(UserData).add(user_data, user_id)

    sql_query = insert(UserData).values(user_data)
    await execute_query(sql_query)


async def __update_user_activity(user_id, activity):
    await get_user(user_id)
    await CashManager(UserData).update(dict(active=activity), user_id)

    query = update(UserData).values(active=activity).filter_by(telegram_id=user_id)
    await execute_query(query)


async def delete_user(user_id):
    await __update_user_activity(user_id, activity=UserActivity.deleted)


async def recover_user(user_id):
    await __update_user_activity(user_id, activity=UserActivity.inactive)
