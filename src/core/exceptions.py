class BaseBotError(Exception):
    def __init__(self, text="Ошибка работы Бота") -> None:
        super().__init__(text)


class DatabaseError(BaseBotError):
    def __init__(self, text="Ошибка при подключении к БД") -> None:
        super().__init__(text)


class UniquenessError(DatabaseError):
    def __init__(self, text="Такая запись уже существует") -> None:
        super().__init__(text)


class DumpError(DatabaseError):
    def __init__(self, text="Ошибка создания дампа базы") -> None:
        super().__init__(text)


class WireguardError(BaseBotError):
    def __init__(
        self, text="Ошибка при выполнении удаленной команды на wireguard сервере"
    ) -> None:
        super().__init__(text)


class PayError(BaseBotError):
    def __init__(self, text="Не оплачена подписка") -> None:
        super().__init__(text)


class StagePayError(PayError):
    def __init__(self, text="Недостаточный уровень подписки") -> None:
        super().__init__(text)


class RedisTypeError(BaseBotError):
    def __init__(
        self, text="Ошибка типа данных при получении или передаче данных в Redis"
    ) -> None:
        super().__init__(text)


class AlreadyDecrementError(BaseBotError):
    def __init__(self, text="Декремент баланса уже происходил сегодня") -> None:
        super().__init__(text)
