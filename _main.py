#!./.venv/bin/python


import asyncio
import logging
import logging.config
import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], "src"))

from src.parser import parse_args

logging.config.fileConfig("log.ini", disable_existing_loggers=False)
logger = logging.getLogger()


def main(args):
    """Точка входа"""

    logger.info("BOT START", extra=args.__dict__)
    asyncio.run(
        {
            "main": noncycle_start_bot,
            "cycle": cycle_start_bot,
        }[args.mode]()
    )
    logger.info("BOT CLOSE")


if __name__ == "__main__":
    args = parse_args()

    from src.app import cycle_start_bot, noncycle_start_bot

    main(args)
