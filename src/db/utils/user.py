import logging
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import insert, select, update

from core.config import settings
from core.metric import async_speed_metric
from db.database import execute_query
from db.models import Transactions, UserActivity, UserData
from db.utils import delete_cash_transactions
from db.utils.redis import CashManager

logger = logging.getLogger()


@async_speed_metric
async def get_user(user_id):
    result: UserData = await CashManager(UserData).get({user_id: ...})
    if result:
        return result[0]

    query = select(UserData).where(UserData.telegram_id == user_id)
    result: UserData = (await execute_query(query)).scalar_one_or_none()
    if result:
        await CashManager(UserData).add({user_id: result.__ustr_dict__})

    return result
    # return DataFrame([getattr(result, "__udict__", UserData().empty)])


@async_speed_metric
async def add_user(user_id, user_name):
    await CashManager(UserData).delete(user_id)

    user_data = dict(telegram_id=user_id, telegram_name=user_name)

    query = insert(UserData).values(user_data).returning(UserData)
    return (await execute_query(query)).scalar_one_or_none()


@async_speed_metric
async def freeze_user(user_id):
    await clear_cash(user_id)

    query = (
        update(UserData)
        .values(active=UserActivity.freezed)
        .filter_by(telegram_id=user_id)
        .returning(UserData)
    )
    await execute_query(query)

    user: UserData = (await execute_query(query)).scalar_one_or_none()

    data = dict(
        user_id=user.telegram_id,
        date=datetime.now(timezone.utc),
        amount=-1 * user.stage * settings.cost,
        withdraw_amount=-1 * user.stage * settings.cost,
        label=uuid4(),
        transaction_id="Заморозка аккаунта",
        transaction_reference="",
    )

    query = insert(Transactions).values(data)
    await execute_query(query)

    await delete_cash_transactions(user.telegram_id)


@async_speed_metric
async def ban_user(user_id):
    await clear_cash(user_id)

    query = (
        update(UserData)
        .values(active=UserActivity.banned)
        .filter_by(telegram_id=user_id)
    )
    await execute_query(query)


@async_speed_metric
async def recover_user(user_id):
    await clear_cash(user_id)

    query = (
        update(UserData)
        .values(active=UserActivity.inactive)
        .filter_by(telegram_id=user_id)
        .returning(UserData)
    )
    result: UserData = (await execute_query(query)).scalar_one_or_none()
    return result


@async_speed_metric
async def update_rate_user(user_id, stage, tax=0, trial=False):
    await clear_cash(user_id)

    tax *= -1

    if trial:
        tax += 7

    query = (
        update(UserData)
        .values(stage=stage, free=False, balance=UserData.balance + tax)
        .filter_by(telegram_id=user_id)
        .returning(UserData)
    )
    result: UserData = (await execute_query(query)).scalar_one_or_none()
    return result


@async_speed_metric
async def clear_cash(user_id):
    await CashManager(None).clear(user_id)
