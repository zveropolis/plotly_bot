import logging
from datetime import datetime

from sqlalchemy import insert, select, update

from core.config import settings
from db.database import execute_query
from db.models import News
from db.utils.redis import CashManager

logger = logging.getLogger()


async def add_news(*news):
    query = insert(News).values(news).returning(News)
    return (await execute_query(query)).scalars().all()
