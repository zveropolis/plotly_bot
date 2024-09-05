import logging

from aiogram import Bot, F, Router
from aiogram.filters.command import Command
from aiogram.types import FSInputFile, Message

import text
from core import exceptions as exc
from core.config import settings
from db import utils

logger = logging.getLogger()
router = Router()


@router.message(Command("admin"))
async def admin_actions(message: Message):
    try:
        user_data = await utils.get_user(message.from_user.id)
    except exc.DatabaseError:
        await message.answer(text.DB_ERROR)
        return

    if user_data.admin[0]:
        await message.answer("Ты админ! (Крутяк)")
    else:
        await message.answer(
            "Данный функционал предназначен для пользования администратором. Если вы администратор, а мы не знаем об этом, отправьте боту секретный пароль."
        )


@router.message(F.text == settings.ADMIN_PASS.get_secret_value())
async def become_an_admin(message: Message, bot: Bot):
    try:
        await utils.set_admin(message.from_user.id)
    except exc.DatabaseError:
        await message.answer(text.DB_ERROR)
    else:
        await message.answer("Вы успешно зарегистрированы как администратор!")
    finally:
        await bot.delete_message(message.from_user.id, message.message_id)


@router.message(Command("dump"))
async def get_dump(message: Message):
    try:
        user_data = await utils.get_user(message.from_user.id)
        if user_data.admin[0]:
            dump = await utils.async_dump()
            await message.answer_document(FSInputFile(dump))
        else:
            await message.answer(
                "Данный функционал предназначен для пользования администратором. Если вы администратор, а мы не знаем об этом, отправьте боту секретный пароль."
            )
    except exc.DumpError as e:
        await message.answer(e.args[0])
    except exc.DatabaseError:
        await message.answer(text.DB_ERROR)
