import logging

from sqlalchemy import update

from db.database import execute_query
from db.models import UserData
from db.utils import CashManager, get_user

logger = logging.getLogger()


async def set_admin(user_id):
    await get_user(user_id)
    await CashManager(UserData).update(dict(admin=True), user_id)

    query = update(UserData).values(admin=True).filter_by(telegram_id=user_id)
    await execute_query(query)
