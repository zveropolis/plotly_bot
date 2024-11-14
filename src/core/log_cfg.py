"""Кастомизация логирования"""

import copy
import logging


class ColoredConsoleHandler(logging.StreamHandler):
    """Обработчик логов, который выводит сообщения в консоль с цветовой кодировкой.

    Этот класс наследует от `logging.StreamHandler` и переопределяет метод `emit`,
    чтобы добавить цветовую кодировку в зависимости от уровня логирования.
    """

    def emit(self, record):
        """Выводит лог-сообщение с цветовой кодировкой.

        Args:
            record (logging.LogRecord): Запись лога, содержащая информацию о сообщении.
        """
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
        myrecord.name = "\x1b[34m" + str(myrecord.name) + "\x1b[0m"
        myrecord.filename = "\x1b[36m" + str(myrecord.filename) + "\x1b[0m"
        myrecord.funcName = "\x1b[36m" + str(myrecord.funcName) + "\x1b[0m"
        try:
            if "METRIC" in myrecord.msg:
                myrecord.msg = myrecord.msg.replace("METRIC", "\x1b[31mMETRIC\x1b[0m")
        except Exception:
            pass
        logging.StreamHandler.emit(self, myrecord)


class ExtraFormatter(logging.Formatter):
    """Форматировщик логов, который добавляет дополнительные атрибуты в формат сообщений.

    Этот класс наследует от `logging.Formatter` и переопределяет метод `format`,
    чтобы включить дополнительные атрибуты, которые могут быть добавлены к записям лога.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Форматирует запись лога, добавляя дополнительные атрибуты.

        Args:
            record (logging.LogRecord): Запись лога, содержащая информацию о сообщении.

        Returns:
            str: Отформатированная строка сообщения лога.
        """
        self._style._fmt = self._fmt
        default_attrs = logging.LogRecord(*[None] * 7).__dict__.keys()
        extras = (
            set(record.__dict__.keys())
            - default_attrs
            - {"message", "color_message", "asctime"}
        )
        if extras:
            format_str = "\n" + "\n".join(f"{val}: %({val})s" for val in sorted(extras))
            self._style._fmt += format_str
        return super().format(record)
