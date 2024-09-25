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

# This module handles user account actions such as registration, deletion, and recovery.


@router.message(Command("reg"))
@router.callback_query(F.data == "register_user")
async def register_user(trigger: Union[Message, CallbackQuery], bot: Bot):
    try:
        # Attempt to add a new user to the database using their ID and full name
        user_data = await utils.add_user(
            trigger.from_user.id, trigger.from_user.full_name
        )
    except exc.UniquenessError as e:
        # Handle uniqueness error (e.g., user already exists)
        await trigger.answer(text=e.args[0], show_alert=True)
    except exc.DatabaseError:
        # Handle general database errors
        await trigger.answer(text=text.DB_ERROR, show_alert=True)
    else:
        # Notify the user of successful registration
        await trigger.answer(text="Поздравляю, регистрация успешна!", show_alert=True)
    finally:
        # Delete the original message after processing to keep the chat clean
        await bot.delete_message(
            trigger.from_user.id, getattr(trigger, "message", trigger).message_id
        )
        # Perform additional account actions after registration
        await account_actions(
            getattr(trigger, "message", trigger),
            user_data=user_data,
            usr_id=trigger.from_user.id,
        )


@router.message(Command("delete"))
@router.callback_query(F.data == "delete_account")
async def delete_user(trigger: Union[Message, CallbackQuery], bot: Bot):
    try:
        # Attempt to delete the user from the database using their ID
        await utils.delete_user(trigger.from_user.id)
    except exc.DatabaseError:
        # Handle database errors during deletion
        await trigger.answer(text=text.DB_ERROR, show_alert=True)
    else:
        # Notify the user that a deletion request is being processed
        await trigger.answer(text="Посылаю запрос на удаление учетной записи...")
    finally:
        # Delete the original message after processing to keep the chat clean
        await bot.delete_message(
            trigger.from_user.id, getattr(trigger, "message", trigger).message_id
        )


@router.message(Command("recover"))
@router.callback_query(F.data == "recover_account")
async def recover_user(trigger: Union[Message, CallbackQuery], bot: Bot):
    try:
        # Attempt to recover the user's account using their ID
        user_data = await utils.recover_user(trigger.from_user.id)
    except exc.DatabaseError:
        # Handle database errors during recovery
        await trigger.answer(text=text.DB_ERROR, show_alert=True)
    else:
        # Notify the user that a recovery request is being processed
        await trigger.answer(text="Посылаю запрос на восстановление учетной записи...")
    finally:
        # Delete the original message after processing to keep the chat clean
        await bot.delete_message(
            trigger.from_user.id, getattr(trigger, "message", trigger).message_id
        )
        # Perform additional account actions after recovery
        await account_actions(
            getattr(trigger, "message", trigger),
            user_data=user_data,
            usr_id=trigger.from_user.id,
        )
