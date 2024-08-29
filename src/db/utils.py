import asyncio
import logging
from ipaddress import ip_interface
from typing import Literal

from pandas import DataFrame
from sqlalchemy import and_, insert, select, update

from db.database import execute_query
from db.models import Transactions, UserActivity, UserData, WgConfig

logger = logging.getLogger()


async def test_base():
    async def __test_base(base):
        query = select(base)
        await execute_query(query)

    return await asyncio.gather(
        *(__test_base(base) for base in (UserData, Transactions, WgConfig)),
        return_exceptions=True,
    )


async def select_user(user_id, extensions: Literal["config", "transact", "all"] = None):
    match extensions:
        case "config":
            query = (
                select(
                    UserData.stage,
                    UserData.active,
                    WgConfig.id,
                    WgConfig.user_private_key,
                    WgConfig.name,
                    WgConfig.address,
                )
                .outerjoin(WgConfig, UserData.telegram_id == WgConfig.user_id)
                .where(UserData.telegram_id == user_id)
            )

        case _:
            query = select(UserData).where(UserData.telegram_id == user_id)

    res = await execute_query(query)
    return DataFrame(data=res.mappings().all())


async def insert_user(user_id, user_name):
    user_data = dict(
        telegram_id=user_id,
        telegram_name=user_name,
        admin=False,
        active=UserActivity.inactive,
        stage=1,
        month=0,
    )

    query = insert(UserData).values(user_data).returning(UserData)

    return await execute_query(query)


async def __update_user_activity(user_id, activity):
    query = update(UserData).values(active=activity).filter_by(telegram_id=user_id)
    await execute_query(query)


async def delete_user(user_id):
    await __update_user_activity(user_id, activity=UserActivity.deleted)


async def recover_user(user_id):
    await __update_user_activity(user_id, activity=UserActivity.inactive)


async def set_admin(user_id):
    query = update(UserData).values(admin=True).filter_by(telegram_id=user_id)
    await execute_query(query)


async def select_wg_config(user_id, cfg_id: list[str] = None):
    query = select(WgConfig).where(WgConfig.user_id == user_id)

    if cfg_id:
        cfg_user_privkey, address = cfg_id
        address = "10.0.0." + address
        query = query.where(
            and_(
                WgConfig.user_private_key.contains(cfg_user_privkey),
                WgConfig.address == ip_interface(address),
            )
        )

    res = await execute_query(query)
    return DataFrame(data=res.mappings().all())


async def insert_wg_config(conf: dict):
    query = insert(WgConfig).values(**conf)

    return await execute_query(query)


async def insert_transaction(conf: dict):
    query = insert(Transactions).values(**conf)

    return await execute_query(query)
