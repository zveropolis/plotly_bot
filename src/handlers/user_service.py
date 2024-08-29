import logging
from typing import Union

from aiogram import Bot, F, Router
from aiogram.filters.command import Command
from aiogram.types import CallbackQuery, Message

import text
from core import exceptions as exc
from db import utils
from src.handlers.account import account_actions

logger = logging.getLogger()
router = Router()


@router.message(Command("reg"))
@router.callback_query(F.data == "register_user")
async def register_user(trigger: Union[Message, CallbackQuery], bot: Bot):
    try:
        await utils.insert_user(trigger.from_user.id, trigger.from_user.full_name)
    except exc.UniquenessError as e:
        await trigger.answer(text=e.args[0], show_alert=True)
    except exc.DatabaseError:
        await trigger.answer(text=text.DB_ERROR, show_alert=True)
    else:
        await trigger.answer(text="Поздравляю, регистрация успешна!", show_alert=True)
    finally:
        await bot.delete_message(
            trigger.from_user.id, getattr(trigger, "message", trigger).message_id
        )
        await account_actions(
            getattr(trigger, "message", trigger),
            usr_id=trigger.from_user.id,
        )


@router.message(Command("delete"))
@router.callback_query(F.data == "delete_account")
async def delete_user(trigger: Union[Message, CallbackQuery], bot: Bot):
    try:
        await utils.delete_user(trigger.from_user.id)
    except exc.DatabaseError:
        await trigger.answer(text=text.DB_ERROR, show_alert=True)
    else:
        await trigger.answer(text="Посылаю запрос на удаление учетной записи...")
    finally:
        await bot.delete_message(
            trigger.from_user.id, getattr(trigger, "message", trigger).message_id
        )


@router.message(Command("recover"))
@router.callback_query(F.data == "recover_account")
async def recover_user(trigger: Union[Message, CallbackQuery], bot: Bot):
    try:
        await utils.recover_user(trigger.from_user.id)
    except exc.DatabaseError:
        await trigger.answer(text=text.DB_ERROR, show_alert=True)
    else:
        await trigger.answer(text="Посылаю запрос на восстановление учетной записи...")
    finally:
        await bot.delete_message(
            trigger.from_user.id, getattr(trigger, "message", trigger).message_id
        )
        await account_actions(
            getattr(trigger, "message", trigger),
            usr_id=trigger.from_user.id,
        )
