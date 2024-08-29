class DatabaseError(Exception):
    def __init__(self, text="Ошибка при подключении к БД") -> None:
        super().__init__(text)


class UniquenessError(DatabaseError):
    def __init__(self, text="Такая запись уже существует") -> None:
        super().__init__(text)


class WireguardError(Exception):
    def __init__(
        self, text="Ошибка при выполнении удаленной команды на wireguard сервере"
    ) -> None:
        super().__init__(text)


class PayError(Exception):
    def __init__(self, text="Не оплачена подписка") -> None:
        super().__init__(text)


class StagePayError(PayError):
    def __init__(self, text="Недостаточный уровень подписки") -> None:
        super().__init__(text)
