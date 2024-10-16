#!./.venv/bin/python


import asyncio
import logging
import logging.config
import os
import sys

import sentry_sdk
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

sys.path.insert(1, os.path.join(sys.path[0], "src"))


from src.parser import parse_args

logging.config.fileConfig("log.ini", disable_existing_loggers=False)
logger = logging.getLogger()


sentry_sdk.init(
    dsn="https://34c9143c835da94d4353ab25d53697c1@o4507927167631360.ingest.de.sentry.io/4508013489619024",
    release="dan-vpn-0.2.0",  # Релизная версия приложения
    environment="dev",  # Возможность добавить среду выполнения
    traces_sample_rate=1.0,
    # send_default_pii=True,
    integrations=[
        AsyncioIntegration(),
        LoggingIntegration(
            level=logging.ERROR,  # Capture info and above as breadcrumbs
            event_level=logging.ERROR,  # Send records as events
        ),
    ],
    profiles_sample_rate=1.0,
    # before_send=USERNAME,
)


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
