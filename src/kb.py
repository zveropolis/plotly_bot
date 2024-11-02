from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from pytils.numeral import get_plural

from db.models import UserActivity, UserData
from text import rates


static_join_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Присоединиться!", callback_data="start_app")]
    ]
)

static_wg_url = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Скачать WireGuard", url="https://www.wireguard.com/install/"
            )
        ]
    ]
)
static_wg_platform_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Windows", callback_data="wg_help_info_Windows_start"
            ),
            InlineKeyboardButton(
                text="Linux", callback_data="wg_help_info_Linux_start"
            ),
            InlineKeyboardButton(
                text="macOS", callback_data="wg_help_info_macOS_start"
            ),
        ],
        [
            InlineKeyboardButton(
                text="Android", callback_data="wg_help_info_Android_start"
            ),
            InlineKeyboardButton(text="iOS", callback_data="wg_help_info_iOS_start"),
        ],
    ]
)

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
            KeyboardButton(text="Перезагрузка"),
            KeyboardButton(text="Статус"),
        ],
        [
            KeyboardButton(text="Подключения"),
            KeyboardButton(text="Подписка"),
            KeyboardButton(text="Помощь"),
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
static_balance_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Пополнить баланс", callback_data="top_up_balance")]
    ]
)

why_freezed_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Почему моя конфигурация заморожена?", callback_data="freeze_info"
            )
        ]
    ]
)
freeze_user_button = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Заморозить аккаунт", callback_data="freeze_account"
            )
        ]
    ]
)


def get_help_menu(name, user_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Что это за сервис?", callback_data="bot_info")],
            [
                InlineKeyboardButton(
                    text="Я первый раз. Что мне делать?",
                    callback_data="first_help_info_start",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Как мне настроить WireGuard?", callback_data="wg_help_info"
                )
            ],
            [
                InlineKeyboardButton(
                    text="У меня тормозит или не работает VPN",
                    callback_data="error_help_info_start",
                )
            ],
            [InlineKeyboardButton(text="Команды", callback_data="cmd_help_info")],
            [
                InlineKeyboardButton(
                    text="Задать свой вопрос",
                    url=f"http://assa.ddns.net/bot/bug/create?name={name}&telegram_id={user_id}",
                )
            ],
        ]
    )


def get_help_book_keyboard(pages: list, page: int, prefix: str):
    prev_page = page - 1
    next_page = page + 1

    if page == 0:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Следующий шаг",
                        callback_data=f"{prefix}_{next_page}",
                    )
                ]
            ]
        )

    if page == len(pages) - 1:
        return InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Предыдущий шаг",
                        callback_data=f"{prefix}_{prev_page}",
                    )
                ],
                [
                    InlineKeyboardButton(
                        text="Покажи весь алгоритм", callback_data=f"{prefix}_all"
                    )
                ],
            ]
        )

    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Предыдущий шаг", callback_data=f"{prefix}_{prev_page}"
                ),
                InlineKeyboardButton(
                    text="Следующий шаг", callback_data=f"{prefix}_{next_page}"
                ),
            ],
        ]
    )


def get_account_keyboard(user_data: UserData):
    buttons = []
    match getattr(user_data, "active", None):
        case UserActivity.active | UserActivity.inactive:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text="Заморозить аккаунт", callback_data="freeze_account_info"
                    )
                ]
            )
        case UserActivity.freezed:
            buttons.append(
                [
                    InlineKeyboardButton(
                        text="Разморозить аккаунт", callback_data="recover_account"
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
            [
                InlineKeyboardButton(text="Мой ID", callback_data="user_id_info"),
                InlineKeyboardButton(text="Помощь", callback_data="main_help"),
            ],
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
                    InlineKeyboardButton(
                        text="История операций", callback_data="transact_history"
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
                    InlineKeyboardButton(
                        text="История операций", callback_data="transact_history"
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
            InlineKeyboardButton(text="100", callback_data="pay_sub_100"),
            InlineKeyboardButton(text="250", callback_data="pay_sub_250"),
            InlineKeyboardButton(text="500", callback_data="pay_sub_500"),
            InlineKeyboardButton(text="1000", callback_data="pay_sub_1000"),
        ]
    ]

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    return keyboard


def get_bug_report_url(name, user_id):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Заполнить форму обращения",
                    url=f"http://assa.ddns.net/bot/bug/create?name={name}&telegram_id={user_id}",
                )
            ]
        ]
    )


def get_pay_url(sum, url):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"Пополнить на {get_plural(sum, 'рубль, рубля, рублей')}",
                    url=url,
                )
            ]
        ]
    )
