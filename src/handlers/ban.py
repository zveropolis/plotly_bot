from aiogram import F, Router
from aiogram.filters.chat_member_updated import KICKED, MEMBER, ChatMemberUpdatedFilter
from aiogram.types import ChatMemberUpdated

import text
from core import exceptions as exc
from db import utils

router = Router()
router.my_chat_member.filter(F.chat.type == "private")


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=KICKED))
async def user_blocked_bot(event: ChatMemberUpdated):
    await utils.ban_user(event.from_user.id)


@router.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER))
async def user_unblocked_bot(event: ChatMemberUpdated):
    try:
        await utils.recover_user(event.from_user.id)
    except exc.DatabaseError:
        await event.answer(text=text.DB_ERROR, show_alert=True)
    else:
        await event.answer(text="Посылаю запрос на восстановление учетной записи...")
