"""Сбор метрик скорости работы"""

import functools
import logging
from time import time

logger = logging.getLogger()


def async_speed_metric(func):
    """Декоратор для измерения времени выполнения асинхронной функции.

    Этот декоратор оборачивает асинхронную функцию и логирует время, затраченное на ее выполнение.

    Args:
        func (Callable): Асинхронная функция, время выполнения которой нужно измерить.

    Returns:
        Callable: Обернутая асинхронная функция с логированием времени выполнения.
    """

    @functools.wraps(func)
    async def wrapper(*args, **kwargs):
        """Обертка для асинхронной функции, измеряющая время выполнения.

        Args:
            *args: Позиционные аргументы для переданной функции.
            **kwargs: Именованные аргументы для переданной функции.

        Returns:
            Any: Результат выполнения обернутой функции.
        """
        start = time()
        result = await func(*args, **kwargs)
        logger.debug(
            f"METRIC::{func.__module__}::{func.__name__}::[  {int((time()-start)*1000):d}  ]msec"
        )
        return result

    return wrapper
