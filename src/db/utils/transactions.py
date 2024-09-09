import logging

from sqlalchemy import insert

from db.database import execute_query
from db.models import Transactions
from db.utils import CashManager

logger = logging.getLogger()


async def insert_transaction(conf: dict):
    await CashManager(Transactions).add(conf, f'{conf["label"]}:{conf["user_id"]}')

    query = insert(Transactions).values(**conf)

    return await execute_query(query)
