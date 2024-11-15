"""Функционал для работы с БД. Новости"""

import logging

from sqlalchemy import delete, insert

from db.database import execute_query
from db.models import News

logger = logging.getLogger()


async def add_news(*news):
    """Добавляет новости в базу данных.

    Удаляет все существующие записи новостей и добавляет новые.

    Args:
        *news (dict): Словари, представляющие новости, которые необходимо добавить в базу данных.

    Returns:
        list[News]: Список объектов News, представляющих добавленные новости.
    """
    query = delete(News)
    await execute_query(query)

    query = insert(News).values(news).returning(News)
    return (await execute_query(query)).scalars().all()
