#!./.venv/bin/python


import argparse
import asyncio
import logging
import logging.config
import logging.handlers
import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], "src"))


from src.app import cycle_start_bot, noncycle_start_bot

logging.config.fileConfig("log.ini", disable_existing_loggers=False)
logging.disable()

logger = logging.getLogger()


def main():
    """Точка входа и парсер аргументов"""
    parser = argparse.ArgumentParser(
        prog="PlotlyBot",
        description="Create Plotly charts in telegram",
        epilog="Plotly bot start script",
    )

    parser.add_argument(
        "-m",
        "--mode",
        type=str,
        choices=["main", "cycle"],
        default="main",
        help="Bot launch mode",
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
        case "console":
            logger.removeHandler(logger.handlers[0])
        case _:
            pass

    logger.info("BOT START", extra=args.__dict__)
    asyncio.run(
        {
            "main": noncycle_start_bot,
            "cycle": cycle_start_bot,
        }[args.mode]()
    )
    logger.info("BOT CLOSE")


if __name__ == "__main__":
    main()
