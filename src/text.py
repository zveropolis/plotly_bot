from dataclasses import dataclass

from pandas import DataFrame

from db.models import UserActivity

me = {"я", "мои данные", "данные", "конфиги", "мои конфиги", "config"}
DB_ERROR = "Ошибка подключения к БД. Обратитесь к администратору."


@dataclass
class AccountStatuses:
    deleted = "Удален"
    admin = "Администратор"
    user = "Пользовательский"


def get_account_status(user_data: DataFrame):
    if user_data.active[0] == UserActivity.deleted:
        return AccountStatuses.deleted
    elif user_data.admin[0]:
        return AccountStatuses.admin
    else:
        return AccountStatuses.user


def get_sub_status(user_data: DataFrame):
    if user_data.active[0] == UserActivity.active:
        return "Активна"
    elif user_data.active[0] == UserActivity.inactive:
        return "Неактивна"
    else:
        return ""
