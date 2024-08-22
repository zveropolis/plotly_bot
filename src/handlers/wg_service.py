import logging
from typing import Union

from aiogram import F, Router, Bot
from aiogram.filters.command import Command
from aiogram.types import Message, CallbackQuery
from aiogram.utils.formatting import Bold, as_list, as_marked_section

import text

logger = logging.getLogger()
router = Router()


@router.message(Command("me"))
@router.message(Command("config"))
@router.message(F.text.lower().in_(text.me))
@router.callback_query(F.data == "user_configurations")
async def get_user_data(trigger: Union[Message, CallbackQuery], bot: Bot):
    if isinstance(trigger, Message):
        await trigger.answer("test1")
    else:
        await trigger.message.answer("test2")
