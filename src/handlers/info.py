import logging

from aiogram import F, Router
from aiogram.filters.command import Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.formatting import Bold, as_list, as_marked_section

from kb import freeze_user_button

logger = logging.getLogger()
router = Router()


@router.message(Command("help"))
@router.message(F.text == "Помощь")
async def help_me(message: Message):
    help_t = as_list(
        "Сообщение вступительное",
        as_marked_section(
            Bold("Алгоритм работы с ботом:"),
            "Запуск (перезагрузка) бота  /start",
            "Данные об аккаунте + быстрый доступ к основным функциям  /account",
            "Список всех команд  /cmd | /commands",
            "/bug - Доложить о баге",
            marker="✅ ",
        ),
        "Готово!",
    )

    await message.answer(**help_t.as_kwargs())


@router.message(Command("time"))
async def started(message: Message, started_at):
    await message.answer(f"Время начала работы бота: {started_at}")


@router.message(Command("id"))
async def start_bot(message: Message):
    await message.answer("Ваш Telegram ID")
    await message.answer(str(message.from_user.id))


@router.message(Command("cmd"))
@router.message(Command("commands"))
@router.message(F.text == "Команды")
async def commands_list(message: Message):
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
            "/refund - Вернуть деньги (ПХААХАХА)",
            "/history - История транзакций",
            marker="~ ",
        ),
        Bold("Информация:"),
        as_marked_section(
            "/help - Помощь",
            "/help_wg - Помощь по настройке wireguard конфигураций на устройствах",
            "/cmd - Список всех команд",
            "/admin - функционал администратора (ЗАПАРОЛИНА)",
            "/bug - Доложить о баге",
            "/id - Ваш Telegram ID",
            "/time - время запуска бота",
            marker="~ ",
        ),
        Bold("Расширенные возможности (тарифы от расширенного и выше):"),
    )

    await message.answer(**help_t.as_kwargs())


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
        reply_markup=freeze_user_button,
    )
