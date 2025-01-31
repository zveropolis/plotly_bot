"""
Модуль для управления различными утилитами базы данных.

Этот модуль содержит функции для работы с администраторами, пользователями,
новостями, отчетами, транзакциями и конфигурациями WireGuard. Он предоставляет
асинхронные методы для выполнения операций, таких как добавление пользователей,
управление их статусами, обработка транзакций и управление конфигурациями.

Импортируемые функции:

- Администраторы:
    - get_admins: Получает список администраторов.
    - get_all_users: Получает всех пользователей.
    - get_valid_users: Получает действительных пользователей.
    - set_admin: Устанавливает пользователя в качестве администратора.

- Новости:
    - add_news: Добавляет новость.

- Отчеты:
    - add_report: Добавляет отчет.

- Транзакции:
    - close_free_trial: Закрывает бесплатный пробный период.
    - confirm_success_pay: Подтверждает успешный платеж.
    - delete_cash_transactions: Удаляет кэшированные транзакции.
    - get_user_transactions: Получает транзакции пользователя.
    - insert_transaction: Вставляет транзакцию.
    - raise_money: Cписывает деньги.

- Пользователи:
    - add_user: Добавляет нового пользователя.
    - ban_user: Блокирует пользователя.
    - clear_cash: Очищает кэш пользователя.
    - freeze_user: Замораживает пользователя.
    - get_user: Получает данные пользователя.
    - mute_user: Отключает уведомления пользователя.
    - recover_user: Восстанавливает пользователя.
    - update_rate_user: Обновляет тариф пользователя.

- Конфигурации WireGuard:
    - add_wg_config: Добавляет конфигурацию WireGuard.
    - freeze_config: Замораживает конфигурацию WireGuard.
    - get_all_wg_configs: Получает все конфигурации WireGuard.
    - get_user_with_configs: Получает пользователя с его конфигурациями.
    - get_wg_config: Получает конфигурацию WireGuard по идентификатору.
    - delete_unregistered_wg_configs: Удаляет из БД конфигурации, которых нет на WG сервере.
"""

from db.utils.admin import (get_admins, get_all_users, get_valid_users,
                            set_admin)
from db.utils.news import add_news
from db.utils.reports import add_report
from db.utils.save import async_backup, dump
from db.utils.tests import test_server_speed
from db.utils.transactions import (close_free_trial, confirm_success_pay,
                                   delete_cash_transactions,
                                   get_user_transactions, insert_transaction,
                                   raise_money)
from db.utils.user import (add_user, ban_user, clear_cash, freeze_user,
                           get_user, mute_user, recover_user, update_rate_user)
from db.utils.wg import (add_wg_config, delete_unregistered_wg_configs,
                         freeze_config, get_all_wg_configs,
                         get_user_with_configs, get_wg_config)
