import logging

import pandas as pd
from aiogram import Bot, F, Router
from aiogram.filters.command import Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.formatting import Bold, as_list, as_marked_section

import text
from db import utils
from kb import get_account_keyboard

logger = logging.getLogger()
router = Router()


@router.message(Command("help"))
async def help_me(message: Message):
    help_t = as_list(
        "Сообщение вступительное",
        as_marked_section(
            Bold("Алгоритм работы с ботом:"),
            "Запустить бота командой /start",
            marker="✅ ",
        ),
        "Готово!",
    )

    await message.answer(**help_t.as_kwargs())
    # await message.answer(
    #     hlink(
    #         "Plotly examples",
    #         "https://plotly.com/python/",
    #     )
    # )


@router.message(Command("time"))
async def started(message: Message, started_at):
    await message.answer(f"Время начала работы бота: {started_at}")


@router.message(Command("me"), Command("config"), F.text.lower().in_(text.me))
async def get_user_data(message: Message):
    user_data = as_list(
        *[f"{key}\t--\t{value}" for key, value in message.from_user.__dict__.items()]
    )

    await message.answer(**user_data.as_kwargs())


@router.message(Command("start"))
async def start_bot(message: Message):
    await message.answer(f"Добро пожаловать, {message.from_user.full_name}!")
    user_data = await utils.select_user(message.from_user.id)

    await account_actions(message, user_data)


@router.message(Command("account"))
async def account_actions(message: Message, user_data: pd.DataFrame = None):
    if user_data is None:
        user_data = await utils.select_user(message.from_user.id)

    account_kb = get_account_keyboard(user_data)

    if user_data.empty:
        await message.answer(
            "Не вижу вас в базе данных. Хотите зарегистрироваться?",
            reply_markup=account_kb,
        )
    else:
        if len(user_data) != 1:
            logger.error(
                "Несколько пользователей имеют одинаковый id", extra=dict(user_data)
            )
        account_status = text.get_account_status(user_data)
        sub_status = text.get_sub_status(user_data)
        account_data = as_list(
            f"Статус аккаунта:  {account_status}",
            f"Статус подписки: {sub_status}" if sub_status else "",
        )

        await message.answer(**account_data.as_kwargs(), reply_markup=account_kb)


@router.callback_query(F.data == "register_user")
async def register_user(callback: CallbackQuery, bot: Bot):
    await utils.insert_user(callback.from_user.id, callback.from_user.full_name)
    await callback.answer(text="Поздравляю, регистрация успешна!", show_alert=True)
    await bot.delete_message(callback.from_user.id, callback.message.message_id)


@router.callback_query(F.data == "delete_account")
async def delete_user(callback: CallbackQuery, bot: Bot):
    await utils.delete_user(callback.from_user.id)
    await callback.answer(text="Аккаунт успешно удален!", show_alert=True)
    await bot.delete_message(callback.from_user.id, callback.message.message_id)


@router.callback_query(F.data == "recover_account")
async def recover_user(callback: CallbackQuery, bot: Bot):
    await utils.recover_user(callback.from_user.id)
    await callback.answer(text="Аккаунт успешно восстановлен!", show_alert=True)
    await bot.delete_message(callback.from_user.id, callback.message.message_id)


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
