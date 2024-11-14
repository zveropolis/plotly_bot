import argparse
import logging

# Настройка логгирования
logger = logging.getLogger()
sql_logger = logging.getLogger("sqlalchemy.engine.Engine")
sched_logger = logging.getLogger("apscheduler")


def parse_args():
    """Парсинг аргументов командной строки.

    Создает парсер аргументов и обрабатывает входные параметры для
    настройки логирования. Поддерживаются следующие параметры:

    - `--nolog`: Опции для отключения логирования:
        - `all`: Отключает все логирование.
        - `file`: Отключает логирование в файл.
        - `console`: Отключает логирование в консоль.

    Returns:
        argparse.Namespace: Объект с аргументами, переданными через командную строку.
    """
    parser = argparse.ArgumentParser(
        prog="DanVPN Bot",
        description="Wireguard config manager",
        epilog="DanVPN bot start script",
    )

    parser.add_argument(
        "--nolog",
        nargs="?",
        const="all",
        choices=["file", "console", "all"],
        help="Unable log",
    )

    args = parser.parse_args()

    match args.nolog:
        case "all":
            logging.disable()
        case "file":
            logger.removeHandler(logger.handlers[1])
            sql_logger.removeHandler(sql_logger.handlers[1])
            sched_logger.removeHandler(sched_logger.handlers[1])
        case "console":
            logger.removeHandler(logger.handlers[0])
            sql_logger.removeHandler(sql_logger.handlers[0])
        case _:
            pass

    return args
