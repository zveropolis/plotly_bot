"""Получение токенов Yoomoney"""

import os
import sys

from yoomoney import Authorize

sys.path.insert(1, os.path.dirname(sys.path[0]))

from core.config import AuthorizeVar, settings


def authorize():
    """Авторизует приложение для работы с API Yoomoney.

    Эта функция создает экземпляр класса Authorize из библиотеки yoomoney,
    используя значения client_id и client_secret, полученные из AuthorizeVar.
    Также устанавливает URL перенаправления и необходимые права доступа (scope).

    Raises:
        Exception: Если авторизация не удалась (например, из-за неверных
        учетных данных или проблем с подключением).
    """
    auth_v = AuthorizeVar()
    Authorize(
        client_id=auth_v.client_id.get_secret_value(),
        client_secret=auth_v.client_secret.get_secret_value(),
        redirect_uri=settings.BOT_URL,
        scope=[
            "account-info",
            "operation-history",
            "operation-details",
            "incoming-transfers",
            # "payment-p2p",
            # "payment-shop",
        ],
    )


if __name__ == "__main__":
    authorize()
