import logging

from pandas import DataFrame
from sqlalchemy import insert, select, update

from core.metric import async_speed_metric
from db.database import execute_query
from db.models import UserActivity, UserData
from db.utils.redis import CashManager

logger = logging.getLogger()


@async_speed_metric
async def get_user(user_id):
    result: UserData = await CashManager(UserData).get({user_id: ...})
    if result:
        return result

    query = select(UserData).where(UserData.telegram_id == user_id)
    result = (await execute_query(query)).scalar_one_or_none()
    if result:
        await CashManager(UserData).add({user_id: result.__ustr_dict__})

    return result
    # return DataFrame([getattr(result, "__udict__", UserData().empty)])


@async_speed_metric
async def add_user(user_id, user_name):
    await CashManager(UserData).delete(user_id)

    user_data = dict(
        telegram_id=user_id,
        telegram_name=user_name,
        admin=False,
        active=UserActivity.inactive,
        stage=1,
        month=0,
    )

    query = insert(UserData).values(user_data).returning(UserData)
    return (await execute_query(query)).scalar_one_or_none()


@async_speed_metric
async def delete_user(user_id):
    await CashManager(UserData).delete(user_id)

    query = (
        update(UserData)
        .values(active=UserActivity.deleted)
        .filter_by(telegram_id=user_id)
    )
    await execute_query(query)


@async_speed_metric
async def recover_user(user_id):
    await CashManager(UserData).delete(user_id)

    query = (
        update(UserData)
        .values(active=UserActivity.inactive)
        .filter_by(telegram_id=user_id)
        .returning(UserData)
    )
    return (await execute_query(query)).scalar_one_or_none()


@async_speed_metric
async def clear_cash(user_id):
    await CashManager(None).clear(user_id)
