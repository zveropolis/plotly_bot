import logging
from datetime import timedelta
from types import NoneType
from typing import Union


from core.config import settings
from core.exceptions import RedisTypeError
from db.database import execute_redis_query, iter_redis_keys, redis_engine
from db.models import Transactions, UserData, WgConfig

# import sentry_sdk


logger = logging.getLogger("redis")


class CashManager:
    class user_id:
        "Класс для аннотации типов"

    redis_types = (bytes, str, int, float, NoneType)

    def __init__(
        self, validation_model: Union[UserData, WgConfig, Transactions]
    ) -> None:
        self.pipe = redis_engine.pipeline()
        self.model = validation_model

    @property
    def cmd(self):
        return self.pipe

    async def __call__(self, *user_id):
        results = await execute_redis_query(self.pipe)

        # await self.update_ttl(user_id)
        validated_results = [
            self.model(**result)
            for result in results
            if result and isinstance(result, dict)
        ]  # TODO а валидирует то только словари получается

        if len(validated_results):
            return validated_results

    def __converter(self, data):
        match data:
            case dict():
                return {
                    key: (value if type(value) in self.redis_types else str(value))
                    for key, value in data.items()
                }
            case list() | tuple():
                return [
                    value if type(value) in self.redis_types else str(value)
                    for value in data
                ]
            case set():
                return {
                    value if type(value) in self.redis_types else str(value)
                    for value in data
                }

    async def add(
        self,
        key_map: dict[user_id, dict | list | tuple | set | str | int | float] = None,
        **mapping: dict[user_id, dict | list | tuple | set | str | int | float],
    ):
        for key, item in key_map.items() if key_map else mapping.items():
            if not item:
                return
            item = self.__converter(item)
            key = f"data:{self.model.__tablename__}:{key}"

            match item:
                case dict():
                    self.pipe.hset(name=key, mapping=item)
                case list() | tuple():
                    self.pipe.rpush(name=key, *item)
                case set():
                    self.pipe.sadd(name=key, *item)
                case str() | int() | float():
                    self.pipe.set(name=key, value=item)

                case _:
                    raise RedisTypeError

            self.pipe.expire(key, timedelta(hours=settings.cash_ttl))
        await execute_redis_query(self.pipe)

    async def get(self, *id_obj: dict | list | tuple | set | str | int | float):
        for key in id_obj:
            match key:
                case dict():
                    self.pipe.hgetall(f"data:{self.model.__tablename__}:{list(key)[0]}")
                case list() | tuple():
                    self.pipe.lrange(f"data:{self.model.__tablename__}:{key[0]}", 0, -1)
                case set():
                    self.pipe.smembers(name=f"data:{self.model.__tablename__}:{key[0]}")
                case str() | int() | float():
                    self.pipe.get(name=f"data:{self.model.__tablename__}:{key}")

                case _:
                    raise RedisTypeError

        return await self.__call__(*id_obj)

    async def delete(self, *keys, fullkey=False):
        if not fullkey:
            keys = [f"data:{self.model.__tablename__}:{key}" for key in keys]
        if keys:
            self.pipe.delete(*keys)
            return await self.__call__()

    async def clear(self, user_id, fullkey=False):
        if not fullkey:
            rkeys = []
            pattern = ":*"
            for n in range(1, 4):
                async for key in await iter_redis_keys(f"data{pattern*n}:{user_id}"):
                    rkeys.append(key)
        if rkeys:
            self.pipe.delete(*rkeys)
            return await self.__call__()
