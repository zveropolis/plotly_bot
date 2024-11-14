#!./.venv/bin/python


import asyncio
import logging
import logging.config

import sentry_sdk
from sentry_sdk.integrations.asyncio import AsyncioIntegration
from sentry_sdk.integrations.logging import LoggingIntegration

from src.parser import parse_args

logging.config.fileConfig("log.ini", disable_existing_loggers=False)
logger = logging.getLogger()


sentry_sdk.init(
    dsn="https://34c9143c835da94d4353ab25d53697c1@o4507927167631360.ingest.de.sentry.io/4508013489619024",
    release="dan-vpn-0.3",  # Релизная версия приложения
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

    logger.info(f"<{'=' * 10} BOT START {'='*10}>", extra=args.__dict__)
    asyncio.run(start_bot())
    logger.info("BOT CLOSE")


if __name__ == "__main__":
    logger.info("\n" * 5 + "#" * 20)

    for extra_logger in {logger.split(".")[0] for logger in logger.manager.loggerDict}:
        logging.getLogger(extra_logger).info(
            f"<{'=' * 10} {extra_logger.upper()} START {'='*10}>"
        )

    args = parse_args()

    from src.app import start_bot

    main(args)
