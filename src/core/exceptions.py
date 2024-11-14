"""Список исключений приложения"""

class BaseBotError(Exception):
    """Базовый класс для ошибок бота.

    Args:
        text (str): Сообщение об ошибке. Defaults to "Ошибка работы Бота".
    """

    def __init__(self, text="Ошибка работы Бота") -> None:
        super().__init__(text)


class DatabaseError(BaseBotError):
    """Ошибка, связанная с работой с базой данных.

    Args:
        text (str): Сообщение об ошибке. Defaults to "Ошибка при подключении к БД".
    """

    def __init__(self, text="Ошибка при подключении к БД") -> None:
        super().__init__(text)


class UniquenessError(DatabaseError):
    """Ошибка, возникающая при попытке создать дублирующую запись.

    Args:
        text (str): Сообщение об ошибке. Defaults to "Такая запись уже существует".
    """

    def __init__(self, text="Такая запись уже существует") -> None:
        super().__init__(text)


class BackupError(DatabaseError):
    """Ошибка, возникающая при создании бэкапа базы данных.

    Args:
        text (str): Сообщение об ошибке. Defaults to "Ошибка создания бэкапа базы".
    """

    def __init__(self, text="Ошибка создания бэкапа базы") -> None:
        super().__init__(text)


class DumpError(DatabaseError):
    """Ошибка, возникающая при создании дампа базы данных.

    Args:
        text (str): Сообщение об ошибке. Defaults to "Ошибка создания дампа базы".
    """

    def __init__(self, text="Ошибка создания дампа базы") -> None:
        super().__init__(text)


class WireguardError(BaseBotError):
    """Ошибка, возникающая при выполнении удаленной команды на сервере WireGuard.

    Args:
        text (str): Сообщение об ошибке. Defaults to "Ошибка при выполнении удаленной команды на wireguard сервере".
    """

    def __init__(
        self, text="Ошибка при выполнении удаленной команды на wireguard сервере"
    ) -> None:
        super().__init__(text)


class PayError(BaseBotError):
    """Ошибка, возникающая при проблемах с оплатой.

    Args:
        text (str): Сообщение об ошибке. Defaults to "Не оплачена подписка".
    """

    def __init__(self, text="Не оплачена подписка") -> None:
        super().__init__(text)


class StagePayError(PayError):
    """Ошибка, возникающая при недостаточном уровне подписки.

    Args:
        text (str): Сообщение об ошибке. Defaults to "Недостаточный уровень подписки".
    """

    def __init__(self, text="Недостаточный уровень подписки") -> None:
        super().__init__(text)


class RedisTypeError(BaseBotError):
    """Ошибка типа данных при работе с Redis.

    Args:
        text (str): Сообщение об ошибке. Defaults to "Ошибка типа данных при получении или передаче данных в Redis".
    """

    def __init__(
        self, text="Ошибка типа данных при получении или передаче данных в Redis"
    ) -> None:
        super().__init__(text)


class AlreadyDecrementError(BaseBotError):
    """Ошибка, возникающая при попытке декремента баланса более одного раза в день.

    Args:
        text (str): Сообщение об ошибке. Defaults to "Декремент баланса уже происходил сегодня".
    """

    def __init__(self, text="Декремент баланса уже происходил сегодня") -> None:
        super().__init__(text)
