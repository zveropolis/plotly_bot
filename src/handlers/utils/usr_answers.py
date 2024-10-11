import logging
from typing import Union

from aiogram.types import CallbackQuery, Message

import kb
import text
from core import exceptions as exc
from db import utils
from db.models import UserActivity, UserData

logger = logging.getLogger()


async def find_user(trigger: Union[Message, CallbackQuery], configs=False):
    try:
        # Retrieve user data from the database
        if configs:
            user_data: UserData = await utils.get_user_with_configs(
                trigger.from_user.id
            )

        else:
            user_data: UserData = await utils.get_user(trigger.from_user.id)

        if user_data is None:
            # If user data is not found, prompt registration
            await getattr(trigger, "message", trigger).answer(
                "Отсутсвуют данные пользователя. Зарегистрируйтесь",
                reply_markup=kb.static_reg_button,
            )
        elif user_data.active == UserActivity.freezed:
            # Notify user if their account is freezed
            await trigger.answer("Аккаунт заморожен", show_alert=True)
            return None
    except exc.DatabaseError:
        # Handle database errors
        await trigger.answer(text=text.DB_ERROR, show_alert=True)
    else:
        return user_data


async def find_config(callback: CallbackQuery):
    *_, cfg_id = callback.message.text.partition("| id: ")
    try:
        # Retrieve the user's configuration from the database
        user_config = await utils.get_wg_config(callback.from_user.id, cfg_id)
    except exc.DatabaseError:
        # Handle database errors
        await callback.answer(text=text.DB_ERROR, show_alert=True)
    else:
        return user_config
