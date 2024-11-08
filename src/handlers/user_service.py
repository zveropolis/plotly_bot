import logging
from typing import Union

from aiogram import Bot, F, Router
from aiogram.filters.command import Command
from aiogram.types import CallbackQuery, Message

from db.models import UserActivity, UserData
import text
from core import exceptions as exc
from db import utils
from src.handlers.account import account_actions

logger = logging.getLogger()
router = Router()
router.message.filter(F.chat.type == "private")


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
        # Perform additional account actions after registration
        await account_actions(
            getattr(trigger, "message", trigger),
            user_data=user_data,
            usr_id=trigger.from_user.id,
        )
    finally:
        # Delete the original message after processing to keep the chat clean
        await bot.delete_message(
            trigger.from_user.id, getattr(trigger, "message", trigger).message_id
        )


@router.message(Command("freeze"))
@router.callback_query(F.data == "freeze_account")
async def freeze_user(trigger: Union[Message, CallbackQuery], bot: Bot):
    try:
        user_data: UserData = await utils.get_user(trigger.from_user.id)
        match user_data.active:
            case UserActivity.freezed:
                await trigger.answer(text="Ваш аккаунт уже заморожен")
                return
            case UserActivity.banned:
                await trigger.answer(text="Ваш аккаунт забанен")
                return
            case UserActivity.deleted:
                await trigger.answer(text="Ваш аккаунт удален")
                return
            case _:
                await utils.freeze_user(trigger.from_user.id)
    except exc.DatabaseError:
        await trigger.answer(text=text.DB_ERROR, show_alert=True)
    else:
        await trigger.answer(text="Посылаю запрос на заморозку учетной записи...")
    finally:
        await bot.delete_message(
            trigger.from_user.id, getattr(trigger, "message", trigger).message_id
        )


@router.message(Command("recover"))
@router.callback_query(F.data == "recover_account")
async def recover_user(trigger: Union[Message, CallbackQuery], bot: Bot):
    try:
        user_data: UserData = await utils.get_user(trigger.from_user.id)
        match user_data.active:
            case UserActivity.banned:
                await trigger.answer(text="Ваш аккаунт забанен")
                return
            case UserActivity.deleted:
                await trigger.answer(text="Ваш аккаунт удален")
                return
            case UserActivity.freezed:
                user_data = await utils.recover_user(trigger.from_user.id)
            case _:
                await trigger.answer(text="Ваш аккаунт уже разморожен")
                return
    except exc.DatabaseError:
        # Handle database errors during recovery
        await trigger.answer(text=text.DB_ERROR, show_alert=True)
    else:
        # Notify the user that a recovery request is being processed
        await trigger.answer(text="Посылаю запрос на разморозку учетной записи...")
        # Perform additional account actions after recovery
        await account_actions(
            getattr(trigger, "message", trigger),
            user_data=user_data,
            usr_id=trigger.from_user.id,
        )
    finally:
        # Delete the original message after processing to keep the chat clean
        await bot.delete_message(
            trigger.from_user.id, getattr(trigger, "message", trigger).message_id
        )
