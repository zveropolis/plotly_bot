"""Определение триггеров и функций в БД"""

import os

from sqlalchemy import DDL, event

from core.config import Base
from core.path import PATH

sql_path = os.path.join(PATH, "src", "db", "sql")
"""str: Путь к директории, содержащей SQL-скрипты."""

with open(os.path.join(sql_path, "_update_user_status.sql")) as sql:
    update_user_status = DDL(sql.read())
    """DDL: SQL-операция для обновления статуса пользователя."""

with open(os.path.join(sql_path, "trigger_update_user_status.sql")) as sql:
    trigger_update_user_status = DDL(sql.read())
    """DDL: Триггер для обновления статуса пользователя."""

with open(os.path.join(sql_path, "_succesful_pay.sql")) as sql:
    succesful_pay = DDL(sql.read())
    """DDL: SQL-операция для обработки успешного платежа."""

with open(os.path.join(sql_path, "trigger_succesful_pay.sql")) as sql:
    trigger_succesful_pay = DDL(sql.read())
    """DDL: Триггер для обработки успешного платежа."""

with open(os.path.join(sql_path, "_unfreeze_configs.sql")) as sql:
    unfreeze_configs = DDL(sql.read())
    """DDL: SQL-операция для размораживания конфигураций."""

with open(os.path.join(sql_path, "_delete_old_transactions.sql")) as sql:
    delete_old_transactions = DDL(sql.read())
    """DDL: SQL-операция для удаления старых транзакций."""

with open(os.path.join(sql_path, "trigger_old_transactions.sql")) as sql:
    trigger_old_transactions = DDL(sql.read())
    """DDL: Триггер для удаления старых транзакций."""

# Подписка на события создания метаданных
event.listen(Base.metadata, "after_create", update_user_status)
"""None: Подписка на событие после создания метаданных для обновления статуса пользователя."""

event.listen(Base.metadata, "after_create", trigger_update_user_status)
"""None: Подписка на событие после создания метаданных для триггера обновления статуса пользователя."""

event.listen(Base.metadata, "after_create", succesful_pay)
"""None: Подписка на событие после создания метаданных для обработки успешного платежа."""

event.listen(Base.metadata, "after_create", trigger_succesful_pay)
"""None: Подписка на событие после создания метаданных для триггера успешного платежа."""

event.listen(Base.metadata, "after_create", unfreeze_configs)
"""None: Подписка на событие после создания метаданных для размораживания конфигураций."""

event.listen(Base.metadata, "after_create", delete_old_transactions)
"""None: Подписка на событие после создания метаданных для удаления старых транзакций."""

event.listen(Base.metadata, "after_create", trigger_old_transactions)
"""None: Подписка на событие после создания метаданных для триггера удаления старых транзакций."""
