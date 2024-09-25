import logging

from sqlalchemy import and_, insert, select
from sqlalchemy.orm import joinedload

from core.metric import async_speed_metric
from db.database import execute_query, iter_redis_keys
from db.models import UserData, WgConfig
from db.utils import get_user
from db.utils.redis import CashManager

logger = logging.getLogger()


@async_speed_metric
async def get_cash_wg_configs(user_id):
    cash = CashManager(WgConfig)

    wg_keys = await iter_redis_keys(f"data:{WgConfig.__tablename__}:*:{user_id}")
    async for wg_conf_key in wg_keys:
        cash.cmd.hgetall(wg_conf_key)

    return await cash(user_id)


@async_speed_metric
async def get_wg_config(user_id, cfg_id: str):
    wg_data: list[WgConfig] = await get_cash_wg_configs(user_id)
    if wg_data:
        for wg_conf in wg_data:
            if wg_conf.user_private_key[:4] == cfg_id:
                return wg_conf

    query = select(WgConfig).where(
        and_(WgConfig.user_id == user_id, WgConfig.user_private_key.contains(cfg_id))
    )

    return (await execute_query(query)).scalar_one_or_none()


@async_speed_metric
async def get_user_with_configs(user_id):
    user_data: UserData = await get_user(user_id)
    wg_data: list[WgConfig] = await get_cash_wg_configs(user_id)
    if wg_data:
        if user_data is not None:
            user_data.configs = wg_data

        return user_data

    query = (
        select(UserData)
        .where(UserData.telegram_id == user_id)
        .options(joinedload(UserData.configs))
    )
    result: UserData = (await execute_query(query)).unique().scalar_one_or_none()
    if result:
        await CashManager(WgConfig).add(
            **{
                f"{config.name}:{user_id}": config.__ustr_dict__
                for config in result.configs
            }
        )

    return result


@async_speed_metric
async def add_wg_config(conf: dict, user_id):
    query = insert(WgConfig).values(**conf)
    await execute_query(query)

    rkeys = await iter_redis_keys(f"data:{WgConfig.__tablename__}:*:{user_id}")
    await CashManager(WgConfig).delete(
        *[key async for key in rkeys],
        fullkey=True,
    )
