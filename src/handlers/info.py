import logging

from aiogram import Router
from aiogram.filters.command import Command
from aiogram.types import Message
from aiogram.utils.formatting import Bold, as_list, as_marked_section

logger = logging.getLogger()
router = Router()


@router.message(Command("help"))
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


@router.message(Command("cmd"))
@router.message(Command("commands"))
async def commands_list(message: Message):
    help_t = as_list(
        Bold("Запуск:"),
        "/start - запуск (перезагрузка) бота",
        Bold("Действия с аккаунтом:"),
        as_marked_section(
            "/account | /app - Основной функционал аккаунта",
            "/reg - Регистрация в БД Бота",
            "/delete - Удалить аккаунт",
            "/recover - Восстановить аккаунт",
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
            "/levelup - Повысить уровень подписки",
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
            "/id - ХЗ пока что",
            "/time - время запуска бота",
            marker="~ ",
        ),
    )

    await message.answer(**help_t.as_kwargs())
