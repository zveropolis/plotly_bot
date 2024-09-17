import logging
import os

import aiofiles
from aiogram import Bot
from pytils.numeral import get_plural

from core import exceptions as exc

# from db.utils import get_user_transactions

logger = logging.getLogger()


async def send_notice(bot: Bot):
    async with aiofiles.open(
        os.path.join(os.path.dirname(__file__), "queue.log")
    ) as file:
        notices = (await file.read()).splitlines()

        for notice in notices.copy():
            date, _type, user_id, message, *extra = notice.strip("\n#|").split("||")

            match _type:
                case "TRANSACTION":
                    try:
                        # assert int(user_id) == 6987832296

                        # transactions = await get_user_transactions(int(user_id))
                        pass
                        # await bot.send_message(
                        #     user_id,
                        #     f'<b>УСПЕШНО!</b> Подписка {stage} уровня на {get_plural(month, 'месяц, месяца, месяцев')} ',
                        # )
                    except AssertionError:
                        continue
                    except exc.DatabaseError:
                        break
                    else:
                        notices.pop(notice.index(notice))

    async with aiofiles.open(
        os.path.join(os.path.dirname(__file__), "queue.log"), "w"
    ) as file:
        await file.write("\n".join(notices))
