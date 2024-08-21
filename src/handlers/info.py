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
            "Запустить бота командой /start",
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


@router.message(Command("me"))
@router.message(Command("config"))
@router.message(F.text.lower().in_(text.me))
async def get_user_data(message: Message):
    user_data = as_list(
        *[f"{key}\t--\t{value}" for key, value in message.from_user.__dict__.items()]
    )

    await message.answer(**user_data.as_kwargs())
