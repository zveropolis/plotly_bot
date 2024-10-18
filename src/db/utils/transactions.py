import logging

from sqlalchemy import and_, insert, select, update

from db.database import execute_query, iter_redis_keys
from db.models import Transactions, UserData
from db.utils.redis import CashManager

logger = logging.getLogger()


async def __clear_transactions(user_id):
    rkeys = await iter_redis_keys(f"data:{Transactions.__tablename__}:*:{user_id}")
    await CashManager(Transactions).delete(
        *[key async for key in rkeys],
        fullkey=True,
    )


async def insert_transaction(conf: dict):
    await __clear_transactions(conf["user_id"])

    query = insert(Transactions).values(**conf)
    await execute_query(query)


async def confirm_success_pay(transaction: Transactions):
    query = select(Transactions).where(Transactions.label == transaction.label)
    prev_result: Transactions = (await execute_query(query)).scalars().first()

    if getattr(prev_result, "transaction_id", None):
        query = (
            insert(Transactions)
            .values(
                user_id=prev_result.user_id,
                date=transaction.date,
                amount=transaction.amount,
                label=transaction.label,
                transaction_id=transaction.transaction_id,
                sha1_hash=transaction.sha1_hash,
                sender=transaction.sender,
                withdraw_amount=transaction.withdraw_amount,
                transaction_reference=prev_result.transaction_reference,
            )
            .returning(Transactions)
        )

    else:
        query = (
            update(Transactions)
            .values(
                date=transaction.date,
                amount=transaction.amount,
                transaction_id=transaction.transaction_id,
                sha1_hash=transaction.sha1_hash,
                sender=transaction.sender,
                withdraw_amount=transaction.withdraw_amount,
            )
            .filter_by(label=transaction.label)
            .returning(Transactions)
        )

    result: Transactions = (await execute_query(query)).scalar_one_or_none()

    if result:
        await __clear_transactions(result.user_id)
        await CashManager(UserData).delete(result.user_id)

    return result


async def close_free_trial(user_id):
    query = (
        update(UserData)
        .values(stage=1)
        .where(and_(UserData.telegram_id == user_id, UserData.stage == 0.3))
        .returning(UserData)
    )

    result: UserData = (await execute_query(query)).scalar_one_or_none()
    return result


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
