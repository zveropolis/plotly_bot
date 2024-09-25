import functools
import logging
from time import time

logger = logging.getLogger()


def async_speed_metric(func):
    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        start = time()
        result = await func(*args, **kwargs)
        logger.debug(
            f"METRIC::{func.__module__}::{func.__name__}::[  {int((time()-start)*1000):d}  ]msec"
        )

        return result

    return wrapper
