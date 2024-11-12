import logging

from sqlalchemy import delete, insert

from db.database import execute_query
from db.models import News

logger = logging.getLogger()


async def add_news(*news):
    query = delete(News)
    await execute_query(query)

    query = insert(News).values(news).returning(News)
    return (await execute_query(query)).scalars().all()
