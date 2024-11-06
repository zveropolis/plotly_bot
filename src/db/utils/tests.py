import asyncio
import logging
from datetime import timedelta

from sqlalchemy import select

from core.exceptions import BaseBotError, WireguardError
from db.database import execute_query, execute_redis_query, redis_engine
from db.models import Transactions, UserData, WgConfig

logger = logging.getLogger()


async def test_base():
    async def __test_base(base):
        query = select(base)
        await execute_query(query)

    return await asyncio.gather(
        *(__test_base(base) for base in (UserData, Transactions, WgConfig)),
        return_exceptions=True,
    )


async def test_redis_base():
    pipe = redis_engine.pipeline()
    pipe.ping()
    pipe.flushdb()

    return await asyncio.gather(
        *(execute_redis_query(pipe),),
        return_exceptions=True,
    )


async def test_server_speed():
    pipe = redis_engine.pipeline()
    pipe.get("data:speedtest:in")
    pipe.get("data:speedtest:out")
    speed_in, speed_out = await execute_redis_query(pipe)
    try:
        if speed_in and speed_out:
            return float(speed_in), float(speed_out)

        cmd = "iperf3 -O 1 -t 5 -Jc 172.31.0.1 | jq '.end.sum_sent.bits_per_second, .end.sum_received.bits_per_second'"

        proc = await asyncio.create_subprocess_shell(
            cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await proc.communicate()

        speed_in, speed_out = stdout.decode().strip("\r\n").split("\n")

        logger.info(
            f"speedtest exited with {proc.returncode}",
            extra={"Server speed_in": speed_in, "Server speed_out": speed_out},
        )

        ERROR = stderr.decode()
        assert not ERROR, "Ошибка измерения пропускной способности"

        pipe = redis_engine.pipeline()
        pipe.set("data:speedtest:in", speed_in)
        pipe.expire("data:speedtest:in", timedelta(minutes=30))

        pipe.set("data:speedtest:out", speed_out)
        pipe.expire("data:speedtest:out", timedelta(minutes=30))
        await execute_redis_query(pipe)

        return float(speed_in), float(speed_out)
    except AssertionError:
        logger.exception(ERROR)
        raise BaseBotError
    except ValueError:
        logger.exception("Ошибка измерения пропускной способности")
        raise BaseBotError
