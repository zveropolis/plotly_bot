import asyncio
import logging
from datetime import datetime, timedelta

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.chat_action import ChatActionMiddleware
from aiohttp import ClientSession
from apscheduler.schedulers.asyncio import AsyncIOScheduler

import handlers as hand
from core.config import settings
from core.err import exception_logging
from db import models, utils  # NOTE for subserver
from db.utils.tests import test_base, test_redis_base
from scheduler.balance import balance_decrement, users_notice
from scheduler.config_freezer import check_freeze_configs
from scheduler.notices import send_notice
from wg.utils import SSH

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
        hand.bug.router,
    )

    return bot, dp


def __create_scheduler(bot):
    scheduler = AsyncIOScheduler()
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
    scheduler.add_job(
        balance_decrement,
        trigger="interval",
        seconds=3600,
        start_date=datetime.now() + timedelta(seconds=20),
    )
    scheduler.add_job(
        users_notice,
        trigger="interval",
        seconds=3600,
        start_date=datetime.now() + timedelta(seconds=30),
        kwargs={"bot": bot},
    )
    scheduler.add_job(
        check_freeze_configs,
        trigger="interval",
        seconds=60,
        start_date=datetime.now() + timedelta(seconds=15),
    )

    return scheduler


async def __start_bot(
    bot: Bot, dp: Dispatcher, scheduler: AsyncIOScheduler, timeout: float = None
):
    await __test_subsystem()

    scheduler.start()

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


async def __test_subsystem():
    bases = await test_base()
    bases.extend(await test_redis_base())
    bases.append(await __test_subserver())

    for base in bases:
        try:
            if isinstance(base, Exception):
                raise base
        except Exception:
            logger.exception("Возникло исключение при подключении к БД")
            raise


async def __test_subserver():
    async with ClientSession() as session:
        # url = "http://assa.ddns.net/test"
        url = "http://127.0.0.1:5000/test"
        params = {"name": "test"}

        async with session.get(url=url, params=params) as response:
            result: dict = await response.json()
            assert result.get("message") == "Hello test"


async def start_bot():
    """Запуск бота"""

    await SSH.connect()

    bot, dp = __create_bot()
    scheduler = __create_scheduler(bot)

    return await __start_bot(bot, dp, scheduler)
