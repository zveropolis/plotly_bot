import logging

from pandas import DataFrame, concat
from numpy import repeat
from sqlalchemy import insert, select

from db.database import execute_query, redis_engine
from db.models import UserData, WgConfig
from db.utils import CashManager, get_user

logger = logging.getLogger()


async def get_cash_wg_configs(user_id):
    cash = CashManager(WgConfig)

    async for wg_conf_key in redis_engine.scan_iter(  # TODO TRY\EXCEPT ZONE
        f"data:{WgConfig.__tablename__}:{user_id}:*"
    ):
        cash.cmd.hgetall(wg_conf_key)

    return await cash(user_id)


async def add_cash_wg_configs(user_id, configs):
    for conf in configs:
        if conf["user_private_key"]:
            validated_conf = WgConfig(**conf).__udict__
            await CashManager(WgConfig).add(
                validated_conf, f'{validated_conf["name"]}:{user_id}'
            )


async def get_wg_config(user_id, cfg_id: list[str] = None):
    wg_data = await get_cash_wg_configs(user_id)
    if not wg_data.empty:
        if cfg_id:
            bad_conf_index = wg_data[
                ~(wg_data["user_private_key"].astype(str).str.startswith(cfg_id))
            ].index
            wg_data.drop(bad_conf_index, inplace=True)

            return wg_data

    query = select(WgConfig).where(WgConfig.user_id == user_id)

    if cfg_id:
        query = query.where(WgConfig.user_private_key.contains(cfg_id))

    result = (await execute_query(query)).mappings().all()

    await add_cash_wg_configs(user_id, result)

    return DataFrame(result)


async def get_users_wg_configs(user_id):
    user_data = await get_user(user_id)
    if user_data.empty:
        return user_data

    wg_data = await get_cash_wg_configs(user_id)

    if not wg_data.empty:
        user_data = DataFrame(
            repeat(user_data.values, len(wg_data), axis=0), columns=user_data.columns
        )
        result = concat([user_data, wg_data], axis=1)

        return result

    query = (
        select(UserData, WgConfig)
        .outerjoin(WgConfig, UserData.telegram_id == WgConfig.user_id)
        .where(UserData.telegram_id == user_id)
    )

    result = (await execute_query(query)).mappings().all()

    await add_cash_wg_configs(user_id, result)

    return DataFrame(result)


async def add_wg_config(conf: dict):
    await CashManager(WgConfig).add(conf, f'{conf["name"]}:{conf["user_id"]}')

    query = insert(WgConfig).values(**conf)
    await execute_query(query)
