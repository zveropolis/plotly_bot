import logging

from sqlalchemy import and_, select, update

from core.metric import async_speed_metric
from db.database import execute_query
from db.models import UserActivity, UserData
from db.utils.redis import CashManager

logger = logging.getLogger()


@async_speed_metric
async def set_admin(user_id):
    await CashManager(UserData).delete(user_id)

    query = (
        update(UserData)
        .values(admin=True)
        .filter_by(telegram_id=user_id)
        .returning(UserData)
    )
    return (await execute_query(query)).scalar_one_or_none()


@async_speed_metric
async def get_all_users(my_id):
    query = select(UserData).where(
        and_(
            UserData.telegram_id != my_id,
            UserData.active != UserActivity.deleted,
        )
    )

    return (await execute_query(query)).scalars().all()
