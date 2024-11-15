"""Функционал для работы с БД. Отчеты и обращения"""

import logging

from sqlalchemy import insert

from core.metric import async_speed_metric
from db.database import execute_query
from db.models import Reports

logger = logging.getLogger()


@async_speed_metric
async def add_report(report: dict):
    """Добавляет новый отчет в базу данных.

    Эта функция принимает словарь, представляющий отчет, и добавляет его в таблицу Reports.
    Возвращает добавленный отчет или None, если добавление не удалось.

    Args:
        report (dict): Словарь, содержащий информацию об отчете, который нужно добавить.

    Returns:
        Reports: Добавленный отчет, если он успешно добавлен, иначе None.
    """
    query = insert(Reports).values(report).returning(Reports)
    result: Reports = (await execute_query(query)).scalar_one_or_none()
    return result
