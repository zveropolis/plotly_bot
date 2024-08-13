import copy
import logging


class ColoredConsoleHandler(logging.StreamHandler):
    def emit(self, record):
        # Need to make a actual copy of the record
        # to prevent altering the message for other loggers
        myrecord = copy.copy(record)
        levelno = myrecord.levelno
        if levelno >= 50:  # CRITICAL / FATAL
            color = "\x1b[31;1m"  # bold_red
        elif levelno >= 40:  # ERROR
            color = "\x1b[31m"  # red
        elif levelno >= 30:  # WARNING
            color = "\x1b[33m"  # yellow
        elif levelno >= 20:  # INFO
            color = "\x1b[32m"  # green
        elif levelno >= 10:  # DEBUG
            color = "\x1b[35m"  # pink
        else:  # NOTSET and anything else
            color = "\x1b[0m"  # normal
        myrecord.levelname = color + str(myrecord.levelname) + "\x1b[0m"  # normal
        logging.StreamHandler.emit(self, myrecord)


class ExtraFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        self._style._fmt = self._fmt

        default_attrs = logging.LogRecord(*[None] * 7).__dict__.keys()
        extras = set(record.__dict__.keys()) - default_attrs - {"message"}
        if extras:
            format_str = "\n" + "\n".join(f"{val}: %({val})s" for val in sorted(extras))
            self._style._fmt += format_str

        return super().format(record)
