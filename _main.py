#!./.venv/bin/python


import asyncio
import logging
import logging.config
import os
import sys

# import sentry_sdk
# from sentry_sdk.integrations.logging import LoggingIntegration
# from sentry_sdk.integrations.asyncio import AsyncioIntegration


sys.path.insert(1, os.path.join(sys.path[0], "src"))


from src.parser import parse_args

logging.config.fileConfig("log.ini", disable_existing_loggers=False)
logger = logging.getLogger()


# sentry_sdk.init(
#     dsn="https://b8e429b4b5f5415244aa3721d587b3b7@o4507927167631360.ingest.de.sentry.io/4507927764664400",
#     release="dan-vpn-0.1.0",  # Релизная версия приложения
#     environment="dev",  # Возможность добавить среду выполнения
#     traces_sample_rate=1.0,
#     send_default_pii=True,
#     enable_tracing=True,
#     # instrumenter="otel",
#     integrations=[
#         AsyncioIntegration(),
#         LoggingIntegration(
#             level=logging.DEBUG,  # Capture info and above as breadcrumbs
#             event_level=logging.DEBUG,  # Send records as events
#         ),
#     ],
#     profiles_sample_rate=1.0,
#     # before_send=USERNAME,
# )


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
