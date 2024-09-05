import logging
from typing import Union

from pandas import DataFrame

from db.database import execute_redis_query, redis_engine
from db.models import UserData, WgConfig, Transactions
from core import exceptions as exc

logger = logging.getLogger()


class CashManager:
    redis_types = (bytes, str, int, float)

    def __init__(self, model: Union[UserData, WgConfig, Transactions]) -> None:
        self.pipe = redis_engine.pipeline()
        self.model = model

    @property
    def cmd(self):
        return self.pipe

    async def __call__(self, query):
        result = await execute_redis_query(self.pipe, query)

        if self.model and result[0]:
            validated_model = self.model(**result[0])
            return DataFrame([validated_model.__udict__])

    def __converter(self, data):
        match data:
            case dict():
                return {
                    key: (value if type(value) in self.redis_types else str(value))
                    for key, value in data.items()
                }
            case list():
                return [
                    value if type(value) in self.redis_types else str(value)
                    for value in data
                ]
            case set():
                return {
                    value if type(value) in self.redis_types else str(value)
                    for value in data
                }

    async def add(self, data: Union[dict, list, set, str], user_id):
        if not data:
            return

        match data:
            case dict():
                data = self.__converter(data)

                self.query = self.pipe.hset(
                    name=f"data:{self.model.__tablename__}:{user_id}",
                    mapping=data,
                )

            case list():
                data = self.__converter(data)

                self.query = self.pipe.rpush(
                    name=f"data:{self.model.__tablename__}:{user_id}", *data
                )
            case set():
                data = self.__converter(data)

                self.query = self.pipe.sadd(
                    name=f"data:{self.model.__tablename__}:{user_id}", *data
                )
            case str() | int() | float():
                self.query = self.pipe.set(
                    name=f"data:{self.model.__tablename__}:{user_id}", value=data
                )

            case _:
                raise exc.RedisTypeError

        await execute_redis_query(self.pipe, self.query)

    async def update(self, data: Union[dict, list, set, str], user_id):
        if not data:
            return

        match data:
            case dict():
                data = self.__converter(data)

                self.query = self.pipe.hset(
                    name=f"data:{self.model.__tablename__}:{user_id}",
                    mapping=data,
                )

            # case list():
            #     data = self.__converter(data)

            #     self.query = self.pipe.rpush(
            #         name=f"data:{self.model.__tablename__}:{user_id}", *data
            #     )
            # case set():
            #     data = self.__converter(data)

            #     self.query = self.pipe.sadd(
            #         name=f"data:{self.model.__tablename__}:{user_id}", *data
            #     )
            case str() | int() | float():
                self.query = self.pipe.set(
                    name=f"data:{self.model.__tablename__}:{user_id}", value=data
                )

            case _:
                raise exc.RedisTypeError

        await execute_redis_query(self.pipe, self.query)

    async def get(self, user_id, _type: Union[dict, list, set, str]):
        match _type:
            case dict():
                self.query = self.pipe.hgetall(
                    f"data:{self.model.__tablename__}:{user_id}"
                )

            case list():
                self.query = self.pipe.lrange(
                    f"data:{self.model.__tablename__}:{user_id}", 0, -1
                )
            case set():
                self.query = self.pipe.smembers(
                    name=f"data:{self.model.__tablename__}:{user_id}"
                )
            case str() | int() | float():
                self.query = self.pipe.get(
                    name=f"data:{self.model.__tablename__}:{user_id}"
                )

            case _:
                raise exc.RedisTypeError

        return await self.__call__(self.query)
