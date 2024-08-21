class DB_error(Exception):
    def __init__(self) -> None:
        super().__init__("Ошибка при подключении к БД")
