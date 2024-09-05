import logging

from sqlalchemy import insert

from db.database import execute_query
from db.models import Transactions

logger = logging.getLogger()


async def insert_transaction(conf: dict):
    query = insert(Transactions).values(**conf)

    return await execute_query(query)
