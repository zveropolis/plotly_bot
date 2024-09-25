import logging

from pandas import DataFrame
from sqlalchemy import insert, select

from db.database import execute_query, iter_redis_keys
from db.models import Transactions
from db.utils.redis import CashManager

logger = logging.getLogger()


async def insert_transaction(conf: dict):
    rkeys = await iter_redis_keys(
        f"data:{Transactions.__tablename__}:*:{conf['user_id']}"
    )
    await CashManager(Transactions).delete(
        *[key async for key in rkeys],
        fullkey=True,
    )

    query = insert(Transactions).values(**conf)
    await execute_query(query)


# async def get_user_transactions(user_id):
#     result = await CashManager(Transactions).get({user_id: ...})

#     if not result.empty:
#         return result

#     query = select(Transactions).where(Transactions.user_id == user_id)

#     result = (await execute_query(query)).mappings().all()

#     await CashManager(Transactions).add(
#         {f'{line["label"]}:{line["user_id"]}': line} for line in map(dict, result)
#     )

#     return DataFrame(result)
