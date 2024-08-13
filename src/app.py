import logging
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.chat_action import ChatActionMiddleware

from core.config import settings
from core.err import exception_logging
from handlers import router

logger = logging.getLogger()


@exception_logging()
async def start(*args, **kwargs):
    """Запуск бота"""

    bot = Bot(
        token=settings.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher(storage=MemoryStorage())  # Данные бота стираются при перезапуске
    dp.message.middleware(ChatActionMiddleware())
    dp.include_router(router)  # Добавка обработчиков
    dp.update(
        dict(
            started_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
        )
    )

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
