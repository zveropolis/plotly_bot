from datetime import timedelta
import logging
from typing import Union

from pandas import DataFrame

from core.exceptions import DatabaseError, RedisTypeError
from db.database import execute_redis_query, redis_engine
from db.models import Transactions, UserData, WgConfig
from redis import exceptions as rexc
from core.config import settings

logger = logging.getLogger()


class CashManager:
    redis_types = (bytes, str, int, float)

    def __init__(
        self, validation_model: Union[UserData, WgConfig, Transactions]
    ) -> None:
        self.pipe = redis_engine.pipeline()
        self.model = validation_model

    @property
    def cmd(self):
        return self.pipe

    async def __call__(self, user_id):
        results = await execute_redis_query(self.pipe)

        await self.update_ttl(user_id)

        return DataFrame(self.model(**result).__udict__ for result in results if result)

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

    async def add(self, data: Union[dict, list, set, str], user_id: str | int):
        if not data:
            return

        match data:
            case dict():
                data = self.__converter(data)

                self.pipe.hset(
                    name=f"data:{self.model.__tablename__}:{user_id}", mapping=data
                )
            case list():
                data = self.__converter(data)

                self.pipe.rpush(
                    name=f"data:{self.model.__tablename__}:{user_id}", *data
                )
            case set():
                data = self.__converter(data)

                self.pipe.sadd(name=f"data:{self.model.__tablename__}:{user_id}", *data)
            case str() | int() | float():
                self.pipe.set(
                    name=f"data:{self.model.__tablename__}:{user_id}", value=data
                )

            case _:
                raise RedisTypeError

        await execute_redis_query(self.pipe)
        await self.update_ttl(user_id)

    async def update(self, data: Union[dict, list, set, str], user_id):
        if not data:
            return

        match data:
            case dict():
                data = self.__converter(data)

                self.pipe.hset(
                    name=f"data:{self.model.__tablename__}:{user_id}",
                    mapping=data,
                )

            # case list():
            #     data = self.__converter(data)

            #     self.pipe.rpush(
            #         name=f"data:{self.model.__tablename__}:{user_id}", *data
            #     )
            # case set():
            #     data = self.__converter(data)

            #     self.pipe.sadd(
            #         name=f"data:{self.model.__tablename__}:{user_id}", *data
            #     )
            case str() | int() | float():
                self.pipe.set(
                    name=f"data:{self.model.__tablename__}:{user_id}", value=data
                )

            case _:
                raise RedisTypeError

        await execute_redis_query(self.pipe)
        await self.update_ttl(user_id)

    async def get(self, user_id, _type: Union[dict, list, set, str]):
        match _type:
            case dict():
                self.pipe.hgetall(f"data:{self.model.__tablename__}:{user_id}")
            case list():
                self.pipe.lrange(f"data:{self.model.__tablename__}:{user_id}", 0, -1)
            case set():
                self.pipe.smembers(name=f"data:{self.model.__tablename__}:{user_id}")
            case str() | int() | float():
                self.pipe.get(name=f"data:{self.model.__tablename__}:{user_id}")

            case _:
                raise RedisTypeError

        return await self.__call__(user_id)

    async def update_ttl(self, user_id):
        try:
            async with redis_engine.pipeline() as pipe:
                async for item in redis_engine.scan_iter(f"*:{user_id}"):
                    pipe.expire(item, timedelta(hours=settings.cash_ttl))

                logquery = pipe.command_stack
                logger.info(f"TRYING TO REDIS QUERY :: {logquery}")
                await pipe.execute()
                logger.info("REDIS QUERY COMPLETED")

        except rexc.AuthenticationError:
            logger.exception(
                f"Ошибка аутентификации при подключении к Redis :: {logquery}"
            )
            raise DatabaseError
        except rexc.ConnectionError:
            logger.exception(f"Ошибка подключения к Redis :: {logquery}")
            raise DatabaseError
        except rexc.TimeoutError:
            logger.exception(
                f"Превышено время ожидания при работе с Redis :: {logquery}"
            )
            raise DatabaseError
        except IndexError:
            logger.exception("Command Stack is empty")
            raise DatabaseError
        except rexc.RedisError:
            logger.exception(f"Произошла неизвестная ошибка c Redis :: {logquery}")
            raise DatabaseError
