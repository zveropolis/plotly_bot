#!./.venv/bin/python


import argparse
import asyncio
import logging
import logging.config
import os
import sys

sys.path.insert(1, os.path.join(sys.path[0], "src"))


from src.app import start

logging.config.fileConfig("log.ini", disable_existing_loggers=False)
# logging.disable()

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
        choices=[
            "main",
        ],
        default="main",
        help="Bot launch mode",
    )

    args = parser.parse_args()

    asyncio.run(start())


if __name__ == "__main__":
    logging.info("MAIN START")  #  extra={"key": "value"}

    main()

    logging.info("MAIN CLOSE")
