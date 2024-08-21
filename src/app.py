import asyncio
import logging
import sys
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.utils.chat_action import ChatActionMiddleware
from git import GitCommandError, Repo

from core.config import settings
from core.err import exception_logging
from core.path import PATH
from db.utils import test_base
from handlers import account, service, info, admin

logger = logging.getLogger()


@exception_logging()
def __create_bot():
    bot = Bot(
        token=settings.bot_token.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    dp = Dispatcher(storage=MemoryStorage())  # Данные бота стираются при перезапуске
    dp.message.middleware(ChatActionMiddleware())
    dp.include_routers(account.router, service.router, info.router, admin.router)

    return bot, dp


async def __start_bot(bot: Bot, dp: Dispatcher, timeout: float = None):
    bases = await test_base()
    for base in bases:
        try:
            if base is not None:
                raise base
        except Exception:
            logger.exception("Возникло исключение при подключении к БД")
            raise

    tasks = await asyncio.wait(
        [
            bot.delete_webhook(drop_pending_updates=True),
            dp.start_polling(
                bot,
                allowed_updates=dp.resolve_used_update_types(),
                started_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
            ),
        ],
        timeout=timeout,
    )
    try:
        await dp.stop_polling()
    except RuntimeError:
        pass
    return tasks


async def noncycle_start_bot():
    """Запуск бота"""

    bot, dp = __create_bot()

    return await __start_bot(bot, dp)


async def cycle_start_bot():
    bot, dp = __create_bot()

    while True:
        try:
            repo = Repo(PATH)
            current = repo.head.commit
            repo.remotes.origin.pull()

        except GitCommandError:
            logger.exception("Ошибка операции git pull")
        else:
            if current != repo.head.commit:
                logger.warning("Зафиксированы изменения в коде. Перезапуск бота.")
                sys.exit(0)
        finally:
            done, pending = await __start_bot(bot, dp, timeout=settings.cycle_duration)

            for task in pending:
                task.cancel()
            pending.clear()
            del task, done

            logger.warning("Перезагрузка")
