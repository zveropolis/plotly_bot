import logging

from aiogram import Bot, F, Router
from aiogram.types import CallbackQuery

import text
from core import exceptions as exc
from db import utils

logger = logging.getLogger()
router = Router()


@router.callback_query(F.data == "register_user")
async def register_user(callback: CallbackQuery, bot: Bot):
    try:
        await utils.insert_user(callback.from_user.id, callback.from_user.full_name)
    except exc.DB_error:
        await callback.answer(text=text.DB_ERROR, show_alert=True)
    else:
        await callback.answer(text="Поздравляю, регистрация успешна!", show_alert=True)
    finally:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)


@router.callback_query(F.data == "delete_account")
async def delete_user(callback: CallbackQuery, bot: Bot):
    try:
        await utils.delete_user(callback.from_user.id)
    except exc.DB_error:
        await callback.answer(text=text.DB_ERROR, show_alert=True)
    else:
        await callback.answer(text="Аккаунт успешно удален!", show_alert=True)
    finally:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)


@router.callback_query(F.data == "recover_account")
async def recover_user(callback: CallbackQuery, bot: Bot):
    try:
        await utils.recover_user(callback.from_user.id)
    except exc.DB_error:
        await callback.answer(text=text.DB_ERROR, show_alert=True)
    else:
        await callback.answer(text="Аккаунт успешно восстановлен!", show_alert=True)
    finally:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
