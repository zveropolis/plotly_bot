from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from pandas import DataFrame

from db.models import UserActivity


def get_account_keyboard(user_data: DataFrame):
    buttons = []
    match user_data.get("active", ["new"])[0]:
        case UserActivity.active | UserActivity.inactive:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text="Удалить аккаунт", callback_data="delete_account"
                    )
                ]
            )
        case UserActivity.deleted:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text="Восстановить аккаунт", callback_data="recover_account"
                    )
                ]
            )
        case _:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text="Зарегистироваться", callback_data="register_user"
                    )
                ]
            )
            return InlineKeyboardMarkup(inline_keyboard=buttons)

    buttons.extend(
        [
            [
                InlineKeyboardButton(
                    text="Мои конфиги", callback_data="user_configurations"
                )
            ],
            [
                InlineKeyboardButton(
                    text="История пополнений", callback_data="user_payment_history"
                )
            ],
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)
