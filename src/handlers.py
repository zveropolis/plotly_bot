import logging

import pandas as pd
from aiogram import Bot, F, Router
from aiogram.filters.command import Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.formatting import as_list

import text
from core import exceptions as exc
from db import utils
from kb import get_account_keyboard

logger = logging.getLogger()
router = Router()


# ===========================================================


# @router.message(F.text.in_({"С пюрешкой", "Без пюрешки"}))
# async def answer(message: Message):
#     await message.answer("Ответ", reply_markup=ReplyKeyboardRemove())


# @router.message(Command("test"))
# async def test(message: Message):
#     import uuid

#     # generate a random UUID

#     random_uuid = uuid.uuid4()

#     # generate a UUID based on a namespace and a name

#     namespace = uuid.NAMESPACE_URL

#     name = "https://example.com"

#     uuid_from_name = uuid.uuid5(namespace, name)

#     # print the UUIDs

#     await message.answer(f"{random_uuid=}\n{uuid_from_name=}")


# @router.message(Command("pay"))
# async def pay(message: Message):
#     token = "YOUR_TOKEN"
#     client = Client(token)

#     quickpay = Quickpay(
#         receiver=client.account_info().account,
#         quickpay_form="shop",
#         targets="Sponsor this project",
#         paymentType="SB",
#         sum=150,
#         label=uuid4(),
#     )
#     print(quickpay.base_url)
#     print(quickpay.redirected_url)
