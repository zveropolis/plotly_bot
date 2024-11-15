"""Ответ по багам"""

import logging
from typing import Union

from aiogram import F, Router
from aiogram.filters.command import Command
from aiogram.types import CallbackQuery, Message

from core.err import bot_exceptor
from kb import get_bug_report_url

logger = logging.getLogger()
router = Router()
router.message.filter(F.chat.type == "private")


@router.message(Command("bug"))
@router.message(Command("refund"))
@router.callback_query(F.data == "call_support")
@bot_exceptor
async def call_support(trigger: Union[Message, CallbackQuery]):
    """Обрабатывает команды /bug и /refund, а также кнопку "call_support".

    Отправляет пользователю сообщение с инструкциями по отчету о проблемах и
    предоставляет ссылку для отправки отчета.

    Args:
        trigger (Union[Message, CallbackQuery]): Сообщение или обратный вызов от пользователя.
        bot (Bot): Экземпляр бота.
    """
    await getattr(trigger, "message", trigger).answer(
        "Сообщите о вашей проблеме. "
        "Желательно приложить скриншоты проблемы. "
        "Если у вас проблемы с оплатой обязательно приложите скриншот совершенной транзакции (чек).",
        reply_markup=get_bug_report_url(
            trigger.from_user.full_name, trigger.from_user.id
        ),
    )
