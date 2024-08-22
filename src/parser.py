import argparse
import logging

logger = logging.getLogger()
sql_logger = logging.getLogger("sqlalchemy.engine.Engine")


def parse_args():
    parser = argparse.ArgumentParser(
        prog="DanVPN Bot",
        description="Wireguard config manager",
        epilog="DanVPN bot start script",
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
            sql_logger.removeHandler(sql_logger.handlers[1])
        case "console":
            logger.removeHandler(logger.handlers[0])
            sql_logger.removeHandler(sql_logger.handlers[0])
        case _:
            pass

    return args
