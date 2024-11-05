import logging
from contextlib import suppress
from typing import Union

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.command import Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.formatting import Bold, as_list, as_marked_section

import kb
import text
from core.exceptions import DatabaseError, WireguardError
from db.models import UserData
from db.utils import test_server_speed
from handlers.utils import find_user
from wg.utils import WgServerTools

logger = logging.getLogger()
router = Router()


async def more_help_info(callback: CallbackQuery):
    await callback.message.answer(
        "Если у вас есть дополнительные вопросы, не стесняйтесь спрашивать! Мы здесь, чтобы помочь вам. 🚀",
        reply_markup=kb.get_help_menu(
            callback.from_user.full_name, callback.from_user.id
        ),
    )


async def change_help_page(message: Message, pages: list, page: int, prefix: str):
    with suppress(TelegramBadRequest):
        await message.edit_text(
            pages[page], reply_markup=kb.get_help_book_keyboard(pages, page, prefix)
        )


async def post_help_book(
    callback: CallbackQuery, book: list, step: str, start_message: str, prefix: str
):
    if step == "start":
        await callback.message.answer(start_message)

        await callback.message.answer(
            book[0],
            reply_markup=kb.get_help_book_keyboard(pages=book, page=0, prefix=prefix),
        )
    elif step.isdigit():
        await change_help_page(
            callback.message, pages=book, page=int(step), prefix=prefix
        )
    else:
        for step in book:
            await callback.message.answer(step)
        await more_help_info(callback)


@router.message(Command("help"))
@router.message(F.text == "Помощь")
@router.callback_query(F.data == "main_help")
async def help_me(trigger: Union[Message, CallbackQuery]):
    await getattr(trigger, "message", trigger).answer(
        "Чем вам помочь?",
        reply_markup=kb.get_help_menu(
            trigger.from_user.full_name, trigger.from_user.id
        ),
    )


@router.callback_query(F.data == "bot_info")
async def bot_info(callback: CallbackQuery):
    await callback.message.answer(text.BOT_INFO, reply_markup=kb.static_join_button)
    await more_help_info(callback)


@router.callback_query(F.data.startswith("first_help_info_"))
async def next_help(callback: CallbackQuery):
    current_step: str = callback.data.split("_")[-1]

    await post_help_book(
        callback,
        book=text.BOT_STEPS,
        step=current_step,
        start_message="🤖 <b>Что делать дальше? Вот краткий алгоритм работы с нашим ботом и WireGuard:</b>",
        prefix="first_help_info",
    )


@router.callback_query(F.data == "wg_help_info")
async def wg_help(callback: CallbackQuery):
    await callback.message.answer(
        "На какую платформу вы хотите установить WireGuard?",
        reply_markup=kb.static_wg_platform_keyboard,
    )


@router.callback_query(F.data.startswith("wg_help_info_"))
async def wg_help_platform(callback: CallbackQuery):
    *_, current_platform, current_step = callback.data.split("_")

    await post_help_book(
        callback,
        book=text.WG_STEPS[current_platform],
        step=current_step,
        start_message=f"🛠️ <b>Настройка WireGuard на {current_platform}:</b>",
        prefix=f"wg_help_info_{current_platform}",
    )


@router.callback_query(F.data.startswith("error_help_info"))
async def error_help(callback: CallbackQuery):
    current_step: str = callback.data.split("_")[-1]

    await post_help_book(
        callback,
        book=text.BOT_ERROR_STEP,
        step=current_step,
        start_message="📋 <b>Не волнуйтесь, вот инструкции по устранению проблем с DanVPN</b>",
        prefix="error_help_info",
    )


@router.message(Command("time"))
async def started(message: Message, started_at):
    await message.answer(f"Время начала работы бота: {started_at}")


@router.message(Command("id"))
@router.callback_query(F.data == "user_id_info")
async def start_bot(trigger: Union[Message, CallbackQuery]):
    await getattr(trigger, "message", trigger).answer("Ваш Telegram ID")
    await getattr(trigger, "message", trigger).answer(str(trigger.from_user.id))


@router.message(Command("cmd"))
@router.message(Command("commands"))
@router.message(F.text == "Команды")
@router.callback_query(F.data == "cmd_help_info")
async def commands_list(trigger: Union[Message, CallbackQuery]):
    help_t = as_list(
        Bold("Запуск:"),
        "/start - запуск (перезагрузка) бота",
        Bold("Действия с аккаунтом:"),
        as_marked_section(
            "/account | /app - Основной функционал аккаунта",
            "/reg - Регистрация в БД Бота",
            "/freeze - Заморозить аккаунт",
            "/recover - Разморозить аккаунт",
            marker="~ ",
        ),
        Bold("Действия с конфигурациями:"),
        as_marked_section(
            "/me | /config - данные о моих конфигурациях wireguard",
            "/create - создать конфигурацию",
            marker="~ ",
        ),
        Bold("Действия с подпиской:"),
        as_marked_section(
            "/sub - Купить подписку",
            "/refund - Сделать запрос на возварт средств",
            "/history - История транзакций",
            marker="~ ",
        ),
        Bold("Информация:"),
        as_marked_section(
            "/help - Помощь",
            "/cmd - Список всех команд",
            "/admin - функционал администратора",
            "/bug - Доложить о баге",
            "/id - Ваш Telegram ID",
            "/time - время запуска бота",
            marker="~ ",
        ),
        as_marked_section(
            Bold("Расширенные возможности (тарифы от расширенного и выше):"),
            "/server - Анализ работы сервера",
            "/speed - Максимально доступная скорость VPN на данный момент",
            "/mute - Отключить уведомления (В РАЗРАБОТКЕ)",
        ),
    )

    await getattr(trigger, "message", trigger).answer(**help_t.as_kwargs())


@router.callback_query(F.data == "freeze_info")
async def freeze_config_info(callback: CallbackQuery):
    await callback.message.answer(
        "Конфигурации замораживаются, когда становятся недоступными. "
        "\n\nПроверьте, достаточно ли средств на вашем счете? Соответсвует ли количество ваших конфигураций вашему тарифу?"
        "Возможно недавно произошли изменения в вашем тарифе, подождите несколько минут и попробуйте снова."
        "\n\nЕсли вам все равно не понятно, почему ваша конфигурация заблокирована, воспользуйтесь командой /bug и сообщите о вашей проблеме."
    )


@router.callback_query(F.data == "freeze_account_info")
async def freeze_user_info(callback: CallbackQuery):
    await callback.message.answer(
        "Заморозка аккаунта подразумевает приостановку ежедневных списаний "
        "и, соответственно, блокировку всех созданных конфигураций."
        "\nРазморозить свой аккаунт можно в меню /app. После разморозки восстановление конфигураций произойдет в течение 1 минуты."
        "\n\n<b>Стоимость услуги равна одному ежедневному списанию вашего тарифа!</b>"
        "\n<b>Разблокировка бесплатна.</b>",
        reply_markup=kb.freeze_user_button,
    )


@router.message(Command("server"))
@router.callback_query(F.data == "server_status")
async def server_status(trigger: Union[Message, CallbackQuery], bot: Bot):
    await bot.send_chat_action(trigger.from_user.id, "typing")

    user_data: UserData = await find_user(trigger)
    if not user_data:
        return
    elif user_data.stage < 2:
        await getattr(trigger, "message", trigger).answer(
            "Команда заблокирована. Выберите тариф от 'Расширенного' или выше."
        )
        return

    try:
        wg = WgServerTools()

        server_status = await wg.get_server_status()
        cpu_usage = await wg.get_server_сpu_usage()

    except WireguardError:
        await getattr(trigger, "message", trigger).answer(text.WG_ERROR)

    else:
        server_data = (
            "Текущие параметры сервера:\n\n"
            f"🖥 Сервер:        <b>{server_status.capitalize()}</b>\n\n"
            f"🦾 СPU usage:  <b>{cpu_usage}</b>"
        )

        await getattr(trigger, "message", trigger).answer(server_data)


@router.message(Command("speed"))
@router.callback_query(F.data == "server_speed")
async def server_speed(trigger: Union[Message, CallbackQuery], bot: Bot):
    await bot.send_chat_action(trigger.from_user.id, "typing")

    user_data: UserData = await find_user(trigger)
    if not user_data:
        return
    elif user_data.stage < 2:
        await getattr(trigger, "message", trigger).answer(
            "Команда заблокирована. Выберите тариф от 'Расширенного' или выше."
        )
        return

    try:
        server_speed_in, server_speed_out = await test_server_speed()

    except WireguardError:
        await getattr(trigger, "message", trigger).answer(
            text.WG_ERROR, show_alert=True
        )
    except DatabaseError:
        await trigger.answer(text=text.DB_ERROR, show_alert=True)
    else:
        server_data = (
            "Текущая максимально доступная скорость интернет соединения по VPN:\n\n"
            f"📥 Скачивание:  <b>{round(float(server_speed_in)/(1048576),2)} Мбит/с</b>\n\n"
            f"📤 Загрузка:         <b>{round(float(server_speed_out)/(1048576),2)} Мбит/с</b>"
        )

        await getattr(trigger, "message", trigger).answer(server_data)
