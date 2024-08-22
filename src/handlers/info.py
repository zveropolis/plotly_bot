import logging

from aiogram import F, Router
from aiogram.filters.command import Command
from aiogram.types import Message
from aiogram.utils.formatting import Bold, as_list, as_marked_section

import text

logger = logging.getLogger()
router = Router()


@router.message(Command("help"))
async def help_me(message: Message):
    help_t = as_list(
        "Сообщение вступительное",
        as_marked_section(
            Bold("Алгоритм работы с ботом:"),
            "Запустить бота командой  /start",
            "Данные об аккаунте + быстрый доступ к основным функциям  /account",
            "Список всех команд  /cmd | /commands",
            marker="✅ ",
        ),
        "Готово!",
    )

    await message.answer(**help_t.as_kwargs())
    # await message.answer(
    #     hlink(
    #         "Plotly examples",
    #         "https://plotly.com/python/",
    #     )
    # )


@router.message(Command("time"))
async def started(message: Message, started_at):
    await message.answer(f"Время начала работы бота: {started_at}")


@router.message(Command("cmd"))
@router.message(Command("commands"))
async def commands_list(message: Message):
    help_t = as_list(
        as_marked_section(
            "/start | /account - основной функционал",
            "/time - время запуска бота",
            "/me | /config - данные о моих конфигурациях wireguard",
            "/",
            marker="~ ",
        ),
    )

    await message.answer(**help_t.as_kwargs())
