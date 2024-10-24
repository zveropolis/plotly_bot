import logging

from sqlalchemy import and_, insert, select, update

from core.metric import async_speed_metric
from db.database import execute_query
from db.models import Reports, UserActivity, UserData
from db.utils.redis import CashManager

logger = logging.getLogger()


@async_speed_metric
async def add_report(report: dict):
    query = insert(Reports).values(report).returning(Reports)
    result: Reports = (await execute_query(query)).scalar_one_or_none()
    return result
