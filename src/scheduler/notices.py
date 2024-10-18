import logging
import os

import aiofiles
from aiogram import Bot
from pytils.numeral import get_plural

from core.path import PATH
from db.models import UserData
from db.utils import close_free_trial, get_admins

logger = logging.getLogger("apscheduler")
logging.getLogger("apscheduler.executors.default").setLevel(logging.WARNING)
queue = os.path.join(PATH, "logs", "queue.log")


async def send_notice(bot: Bot):
    async with aiofiles.open(queue) as file:
        notices = (await file.read()).splitlines()

    for notice in notices.copy():
        date, _type, user_id, label, amount, *extra = notice.strip("\n#|").split("||")
        try:
            match _type:
                case "TRANSACTION":
                    user_id = int(user_id)
                    admin_ids: list[UserData] = await get_admins()

                    await bot.send_message(
                        user_id,
                        f"<b>УСПЕШНО!</b> Ваш баланс пополнен на {get_plural(float(amount), 'рубль, рубля, рублей')}!",
                    )
                    for admin in admin_ids:
                        await bot.send_message(
                            admin.telegram_id,
                            f"Казна пополнена на {get_plural(float(amount), 'рубль, рубля, рублей')} пользователем {user_id}!",
                        )

                    user_data: UserData = await close_free_trial(user_id)
                    if user_data:
                        await bot.send_message(
                            user_id,
                            "Ваш <b>Пробный тариф</b> автоматически сменен на <b>Базовый</b>",
                        )

                    logger.info(
                        "Отправлено сообщение об успешной оплате",
                        extra={"user_id": user_id},
                    )

                case "REPORT":
                    admin_ids: list[UserData] = await get_admins()

                    for admin in admin_ids:
                        await bot.send_message(
                            admin.telegram_id,
                            f"Поступило обращение от пользователя {user_id}. Номер обращения: {label}",
                        )
        except Exception:
            logger.exception("Ошибка планировщика событий")
            continue
        else:
            notices.pop(notice.index(notice))

    async with aiofiles.open(queue, "w") as file:
        await file.write("\n".join(notices))
