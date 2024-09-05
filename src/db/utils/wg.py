import logging
from ipaddress import ip_interface

from pandas import DataFrame
from sqlalchemy import and_, insert, select

from db.database import execute_query
from db.models import Transactions, UserData, WgConfig

logger = logging.getLogger()


async def get_wg_config(user_id, cfg_id: list[str] = None):
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


async def get_users_wg_configs(user_id):
    query = (
        select(UserData, WgConfig)
        .outerjoin(WgConfig, UserData.telegram_id == WgConfig.user_id)
        .where(UserData.telegram_id == user_id)
    )

    result = (await execute_query(query)).mappings().all()

    return DataFrame(result)


async def add_wg_config(conf: dict):
    query = insert(WgConfig).values(**conf)

    return await execute_query(query)
