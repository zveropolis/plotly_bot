import logging
import os

import aiofiles
from aiogram import Bot
from pytils.numeral import get_plural

from core.path import PATH


logger = logging.getLogger("apscheduler")
logging.getLogger("apscheduler.executors.default").setLevel(logging.WARNING)
queue = os.path.join(PATH, "logs", "queue.log")


async def send_notice(bot: Bot):
    async with aiofiles.open(queue) as file:
        notices = (await file.read()).splitlines()

    for notice in notices.copy():
        date, _type, user_id, label, month, stage, *extra = notice.strip("\n#|").split(
            "||"
        )

        match _type:
            case "TRANSACTION":
                try:
                    assert int(user_id)

                    await bot.send_message(
                        user_id,
                        f"<b>УСПЕШНО!</b> Подписка {stage} уровня на {get_plural(int(month), 'месяц, месяца, месяцев')} оплачена!",
                    )
                    logger.info(
                        "Отправлено сообщение об успешной оплате",
                        extra={"user_id": user_id},
                    )
                except Exception:
                    logger.exception("Ошибка планировщика событий")
                    continue
                else:
                    notices.pop(notice.index(notice))

    async with aiofiles.open(queue, "w") as file:
        await file.write("\n".join(notices))
