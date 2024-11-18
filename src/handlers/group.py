"""Действия в чате"""

from aiogram import Bot, F, Router
from aiogram.filters.chat_member_updated import (ADMINISTRATOR, IS_NOT_MEMBER,
                                                 MEMBER,
                                                 ChatMemberUpdatedFilter)
from aiogram.types import ChatMemberUpdated, Message

from core.config import settings
from core.err import bot_except

router = Router()
router.my_chat_member.filter(F.chat.type.in_({"group", "supergroup"}))
router.message.filter(F.chat.type != "private")
chats_variants = {"group": "группу", "supergroup": "супергруппу"}


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER >> ADMINISTRATOR)
)
@bot_except
async def bot_added_as_admin(event: ChatMemberUpdated):
    """Обработчик события, когда бот добавлен в чат как администратор.

    Args:
        event (ChatMemberUpdated): Событие, содержащее информацию о изменении статуса участника.
    """
    await event.answer(
        text=f"Привет! Спасибо, что добавили меня в "
        f'{chats_variants[event.chat.type]} "{event.chat.title}" '
        f"как администратора. ID чата: {event.chat.id}"
    )


@router.my_chat_member(
    ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER >> MEMBER)
)
@bot_except
async def bot_added_as_member(event: ChatMemberUpdated, bot: Bot):
    """Обработчик события, когда бот добавлен в чат как участник.

    Args:
        event (ChatMemberUpdated): Событие, содержащее информацию о изменении статуса участника.
        bot (Bot): Экземпляр бота для выполнения действий.
    """
    chat_info = await bot.get_chat(event.chat.id)
    if chat_info.permissions.can_send_messages:
        await event.answer(
            text=f"Привет! Спасибо, что добавили меня в "
            f'{chats_variants[event.chat.type]} "{event.chat.title}" '
            f"как обычного участника. ID чата: {event.chat.id}"
        )


@router.chat_member(
    ChatMemberUpdatedFilter(member_status_changed=IS_NOT_MEMBER >> MEMBER)
)
@bot_except
async def new_members_hi(event: ChatMemberUpdated):
    """Обработчик события, когда новый участник присоединяется к чату.

    Args:
        event (ChatMemberUpdated): Событие, содержащее информацию о новом участнике.
    """
    await event.answer(
        f"Добро пожаловать в чат нашего VPN сервиса, {event.new_chat_member.user.first_name}. 🫡\n\n"
        "Здесь вы можете задавать интересующие вас вопросы, "
        "общаться с другими клиентами и авторами сервиса, "
        "а также следить за актуальными новостями и обновлениями сервиса",
    )


@router.message(F.text)
@bot_except
async def leave_group(message: Message):
    """Обработчик текстовых сообщений, который выводит бота из группы.

    Args:
        message (Message): Сообщение, содержащее текст.
    """
    if message.chat.id != settings.BOT_CHAT:
        await message.chat.leave()
