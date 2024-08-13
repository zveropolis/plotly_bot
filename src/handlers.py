from aiogram import Router, types
from aiogram.filters.command import Command
from aiogram.utils.formatting import Bold, as_list, as_marked_section
from aiogram.utils.markdown import hlink

router = Router()


@router.message(Command("help"))
async def help_me(message: types.Message):
    help_t = as_list(
        "Данный бот является средством визуализации данных средствами фреймворка Plotly.",
        as_marked_section(
            Bold("Алгоритм работы с ботом:"),
            "Запустить бота командой /start",
            marker="✅ ",
        ),
        "Готово!",
    )

    await message.answer(**help_t.as_kwargs())
    await message.answer(
        hlink(
            "Plotly examples",
            "https://plotly.com/python/",
        )
    )


@router.message(Command("time"))
async def started(message: types.Message):
    await message.answer(f"Время начала работы бота: {message.date}")
