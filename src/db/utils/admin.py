import logging

from sqlalchemy import update

from db.database import execute_query
from db.models import UserData

logger = logging.getLogger()


async def set_admin(user_id):
    query = update(UserData).values(admin=True).filter_by(telegram_id=user_id)
    await execute_query(query)
