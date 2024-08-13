import logging

from core.err import exception_logging

logger = logging.getLogger()


@exception_logging()
def func():
    """Первая функция"""
    ...
