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


@router.message(Command("bug"))
@router.callback_query(F.data == "call_support")
async def call_support(trigger: Union[Message, CallbackQuery], bot: Bot):
    await getattr(trigger, "message", trigger).answer(
        "Сообщите о вашей проблеме. "
        "Желательно приложить скриншоты проблемы. "
        "Если у вас проблемы с оплатой обязательно приложите скриншот совершенной транзакции (чек)."
    )
    await getattr(trigger, "message", trigger).answer(
        "Как только закончите, введите команду /send_bug"
    )
