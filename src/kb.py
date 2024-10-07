from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from pytils.numeral import get_plural

from db.models import UserActivity, UserData
from text import rates

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

static_support_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Доложить о проблеме", callback_data="call_support")]
    ]
)


def get_account_keyboard(user_data: UserData):
    buttons = []
    match getattr(user_data, "active", None):
        case UserActivity.active | UserActivity.inactive:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text="Заморозить аккаунт", callback_data="freeze_account"
                    )
                ]
            )
        case UserActivity.freezed:
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


# def get_pay_keyboard(month, stage):
#     buttons = [
#         [
#             InlineKeyboardButton(text="-1 мес.", callback_data="month_decr"),
#             InlineKeyboardButton(text="+1 мес.", callback_data="month_incr"),
#         ],
#         [
#             InlineKeyboardButton(text="-1 ур.", callback_data="stage_decr"),
#             InlineKeyboardButton(text="+1 ур.", callback_data="stage_incr"),
#         ],
#         [
#             InlineKeyboardButton(
#                 text=f"Оплатить {get_plural(stage, 'уровень, уровня, уровней')} подписки на {get_plural(month, 'месяц, месяца, месяцев')}",
#                 callback_data="pay_sub",
#             )
#         ],
#     ]
#     keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
# return keyboard


def get_subscr_buttons(user_data: UserData, force_rates=False):
    buttons = []
    my_rate = rates.get(user_data.stage, None)
    if my_rate or force_rates:
        for key, rate in rates.items():
            if rate == my_rate:
                prefix = "✅ "
            elif not user_data.free and key == 0.3:
                prefix = "❌ "
            else:
                prefix = ""

            buttons.append(
                [
                    InlineKeyboardButton(
                        text=f"{prefix}{rate} тариф", callback_data=f"rate_info_{key}"
                    )
                ]
            )
        if not force_rates:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text="Пополнить баланс", callback_data="top_up_balance"
                    ),
                ],
            )
    else:
        buttons.extend(
            [
                [
                    InlineKeyboardButton(
                        text="Выбрать тариф", callback_data="change_rate"
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Пополнить баланс", callback_data="top_up_balance"
                    ),
                ],
            ]
        )

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_rate_button(rate: int):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Выбрать этот тариф", callback_data=f"accept_rate_{rate}"
                )
            ]
        ]
    )


def get_pay_keyboard():
    buttons = [
        [
            InlineKeyboardButton(text="1", callback_data="balance_1"),
            InlineKeyboardButton(text="2", callback_data="balance_2"),
            InlineKeyboardButton(text="3", callback_data="balance_3"),
        ],
        [
            InlineKeyboardButton(text="4", callback_data="balance_4"),
            InlineKeyboardButton(text="5", callback_data="balance_5"),
            InlineKeyboardButton(text="6", callback_data="balance_6"),
        ],
        [
            InlineKeyboardButton(text="7", callback_data="balance_7"),
            InlineKeyboardButton(text="8", callback_data="balance_8"),
            InlineKeyboardButton(text="9", callback_data="balance_9"),
        ],
        [
            InlineKeyboardButton(text="0", callback_data="balance_0"),
            InlineKeyboardButton(text="<", callback_data="balance_incr"),
            InlineKeyboardButton(text="<<<", callback_data="balance_clear"),
        ],
        [
            InlineKeyboardButton(text="Пополнить", callback_data="pay_sub"),
        ],
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard
