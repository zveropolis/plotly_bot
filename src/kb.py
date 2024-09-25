from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from pandas import DataFrame
from pytils.numeral import get_plural

from db.models import UserActivity, UserData

static_reg_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Зарегистироваться", callback_data="register_user")]
    ]
)
static_pay_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Купить подписку", callback_data="user_payment")]
    ]
)
static_start_button = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Статус"),
            KeyboardButton(text="Конфигурации"),
            KeyboardButton(text="Подписка"),
        ],
        [
            KeyboardButton(text="Помощь"),
            KeyboardButton(text="Команды"),
        ],
    ],
    resize_keyboard=True,
    input_field_placeholder="Выберете действие или введите команду",
)


def get_account_keyboard(user_data: UserData):
    buttons = []
    match getattr(user_data, "active", None):
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
                    text="Мои конфигурации", callback_data="user_configurations"
                )
            ],
            [InlineKeyboardButton(text="Подписка", callback_data="user_payment")],
        ]
    )

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_config_keyboard():
    buttons = []
    cfgs = []

    cfgs.append(
        [
            InlineKeyboardButton(text="TEXT", callback_data="create_conf_text"),
            InlineKeyboardButton(text="QR", callback_data="create_conf_qr"),
            InlineKeyboardButton(text="FILE", callback_data="create_conf_file"),
        ]
    )

    buttons.append(
        [
            InlineKeyboardButton(
                text="Создать конфигурацию", callback_data="create_configuration"
            ),
        ]
    )
    return (
        InlineKeyboardMarkup(inline_keyboard=buttons),
        InlineKeyboardMarkup(inline_keyboard=cfgs),
    )


def get_pay_keyboard(month, stage):
    buttons = [
        [
            InlineKeyboardButton(text="-1 мес.", callback_data="month_decr"),
            InlineKeyboardButton(text="+1 мес.", callback_data="month_incr"),
        ],
        [
            InlineKeyboardButton(text="-1 ур.", callback_data="stage_decr"),
            InlineKeyboardButton(text="+1 ур.", callback_data="stage_incr"),
        ],
        [
            InlineKeyboardButton(
                text=f"Оплатить {get_plural(stage, 'уровень, уровня, уровней')} подписки на {get_plural(month, 'месяц, месяца, месяцев')}",
                callback_data="pay_sub",
            )
        ],
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
