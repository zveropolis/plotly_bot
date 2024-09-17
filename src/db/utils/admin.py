import logging

from sqlalchemy import update, select, and_

from db.database import execute_query
from db.models import UserData, UserActivity
from db.utils.redis import CashManager
from core.metric import async_speed_metric

logger = logging.getLogger()


@async_speed_metric
async def set_admin(user_id):
    await CashManager(UserData).delete(user_id)

    query = update(UserData).values(admin=True).filter_by(telegram_id=user_id)
    await execute_query(query)


@async_speed_metric
async def get_all_users(my_id):
    query = select(UserData).where(
        and_(
            UserData.telegram_id != my_id,
            UserData.active != UserActivity.deleted,
        )
    )

    return (await execute_query(query)).scalars().all()
