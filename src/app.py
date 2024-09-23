import asyncio
import logging
from datetime import datetime, timedelta

import asyncssh
from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.chat_action import ChatActionMiddleware
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import handlers as hand
from core.config import settings
from core.err import exception_logging
from db.utils.tests import test_base, test_redis_base
from notices.pay import send_notice

logger = logging.getLogger()


@exception_logging()
def __create_bot():
    bot = Bot(
        token=settings.BOT_TOKEN.get_secret_value(),
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )

    storage = RedisStorage.from_url(
        settings.CASHBASE_URL,
        state_ttl=timedelta(hours=settings.cash_ttl),
        data_ttl=timedelta(hours=settings.cash_ttl),
    )

    scheduler = AsyncIOScheduler(timezone="Europe/Moscow")
    scheduler.add_job(
        send_notice,
        # trigger="cron",
        trigger="interval",
        seconds=3,
        # hour=00,
        # minute=00,
        # second=2,
        start_date=datetime.now() + timedelta(seconds=10),
        kwargs={"bot": bot},
    )

    # dp = Dispatcher(storage=MemoryStorage())  # Данные бота стираются при перезапуске
    dp = Dispatcher(storage=storage)
    dp.message.middleware(ChatActionMiddleware())
    dp.include_routers(
        hand.admin.router,
        hand.account.router,
        hand.user_service.router,
        hand.info.router,
        hand.wg_service.router,
        hand.payment.router,
    )

    return bot, dp, scheduler


async def __start_bot(bot: Bot, dp: Dispatcher, timeout: float = None):
    bases = await test_base()
    bases.extend(await test_redis_base())

    for base in bases:
        try:
            if isinstance(base, Exception):
                raise base
        except Exception:
            logger.exception("Возникло исключение при подключении к БД")
            raise

    async with asyncssh.connect(
        settings.WG_HOST,
        username=settings.WG_USER,
        client_keys=settings.WG_KEY.get_secret_value(),
    ) as conn:
        tasks = await asyncio.wait(
            [
                bot.delete_webhook(drop_pending_updates=True),
                dp.start_polling(
                    bot,
                    allowed_updates=dp.resolve_used_update_types(),
                    started_at=datetime.now().strftime("%Y-%m-%d %H:%M"),
                    wg_connection=conn,
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

    bot, dp, scheduler = __create_bot()

    # scheduler.start()
    return await __start_bot(bot, dp)


async def cycle_start_bot():
    bot, dp, scheduler = __create_bot()

    while True:
        scheduler.start()
        done, pending = await __start_bot(bot, dp, timeout=settings.cycle_duration)

        for task in pending:
            task.cancel()
        pending.clear()

        logger.warning("Перезагрузка")
