import logging
from contextlib import suppress
from datetime import datetime
from typing import Union
from uuid import uuid4

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.filters.command import Command
from aiogram.types import CallbackQuery, Message
from aiogram.utils.markdown import hlink
from pytils.numeral import get_plural
from requests.exceptions import ConnectionError
from yoomoney import Client, Quickpay

import text
from core import exceptions as exc
from core.config import settings
from db import utils
from kb import get_pay_keyboard, static_reg_button
from states import Service

logger = logging.getLogger()
router = Router()


@router.message(Command("sub"))
@router.callback_query(F.data == "user_payment")
async def subscribe_manager(trigger: Union[Message, CallbackQuery], state: FSMContext):
    try:
        user_data = await utils.get_user(trigger.from_user.id)

        if user_data.empty:
            await getattr(trigger, "message", trigger).answer(
                "Отсутсвуют данные пользователя. Зарегистрируйтесь",
                reply_markup=static_reg_button,
            )
            return
    except exc.DatabaseError:
        await trigger.answer(text=text.DB_ERROR, show_alert=True)
    else:
        sub_status = text.get_sub_status(user_data)

        if sub_status:
            await state.set_state(Service.sub)
            await state.update_data({"sub": {"month": 1, "stage": 1}})

            await getattr(trigger, "message", trigger).answer(
                "\n".join(
                    (
                        f"Ваша подписка: <b>{sub_status}</b>",
                        f"Актуальная стоимость 1 уровня подписки за 1 месяц: <b>{get_plural(settings.cost, 'рубль, рубля, рублей')}</b>",
                        f"Допустимое количество создаваемых конфигураций на 1 уровень подписки: <b>{settings.acceptable_config}</b>",
                        "(Одна конфигурация может быть подключена к нескольким устройствам, однако такие подключения не могут быть одновременными, поэтому рекомендуется создавать по одной конфигурации на каждое устройство)",
                    )
                )
            )
            await getattr(trigger, "message", trigger).answer(
                f"""Выберите уровень подписки
Текущий:
    1 месяц
    1 уровень
Итоговая стоимость = <b>{get_plural(settings.cost, 'рубль, рубля, рублей')}</b>""",
                reply_markup=get_pay_keyboard(month=1, stage=1),
            )

        else:
            await getattr(trigger, "message", trigger).answer("Аккаунт удален")


@router.callback_query(F.data.startswith("stage_"))
@router.callback_query(F.data.startswith("month_"))
async def edit_sub_stage(callback: CallbackQuery, bot: Bot, state: FSMContext):
    try:
        user_sub_param = (await state.get_data())["sub"]
    except KeyError:
        await callback.answer("Истек срок давности сообщения")
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    else:
        match callback.data:
            case "stage_incr":
                user_sub_param["stage"] += 1
                await update_stage_text(callback.message, user_sub_param)
                await state.update_data({"sub": user_sub_param})

            case "stage_decr":
                if user_sub_param["stage"] > 1:
                    user_sub_param["stage"] -= 1
                await update_stage_text(callback.message, user_sub_param)
                await state.update_data({"sub": user_sub_param})

            case "month_incr":
                user_sub_param["month"] += 1
                await update_stage_text(callback.message, user_sub_param)
                await state.update_data({"sub": user_sub_param})

            case "month_decr":
                if user_sub_param["month"] > 1:
                    user_sub_param["month"] -= 1
                await update_stage_text(callback.message, user_sub_param)
                await state.update_data({"sub": user_sub_param})

        await callback.answer()


async def update_stage_text(message: Message, user_sub_param: dict):
    new_val_month = user_sub_param["month"]
    new_val_stage = user_sub_param["stage"]
    SUM = settings.cost * new_val_stage * new_val_month * 1.03

    with suppress(TelegramBadRequest):
        await message.edit_text(
            f"""Выберите уровень подписки
Текущий:
    {get_plural(new_val_month,'месяц, месяца, месяцев')}
    {get_plural(new_val_stage, 'уровень, уровня, уровней')}
Итоговая стоимость = <b>{get_plural(SUM, 'рубль, рубля, рублей')}</b>""",
            reply_markup=get_pay_keyboard(month=new_val_month, stage=new_val_stage),
        )


@router.callback_query(F.data == "pay_sub")
async def pay(callback: CallbackQuery, bot: Bot, state: FSMContext):
    try:
        user_sub = (await state.get_data())["sub"]
        user_month = user_sub["month"]
        user_stage = user_sub["stage"]
        client = Client(settings.YOO_TOKEN.get_secret_value())
        transaction_label = uuid4()

        SUM = settings.cost * user_stage * user_month * 1.03

        quickpay = Quickpay(
            receiver=client.account_info().account,
            quickpay_form="shop",
            targets=f"Sponsor this project ({user_month} month | {user_stage} stage)",
            paymentType="SB",
            sum=SUM,
            label=transaction_label,
        )

        await utils.insert_transaction(
            dict(
                user_id=callback.from_user.id,
                transaction_reference=quickpay.base_url,
                transaction_label=transaction_label,
                transaction_date=datetime.today(),
                transaction_sum=SUM,
                transaction_stage=user_stage,
                transaction_month=user_month,
            )
        )

        await callback.message.answer(
            hlink(
                f"Оплатить подписку за {get_plural(SUM, 'рубль, рубля, рублей')} (Ссылка №1)",
                quickpay.base_url,
            )
        )
        await callback.message.answer(
            hlink(
                f"Оплатить подписку за {get_plural(SUM, 'рубль, рубля, рублей')} (Ссылка №2)",
                quickpay.redirected_url,
            )
        )
        await state.clear()

    except KeyError:
        await callback.answer("Истек срок давности сообщения")
    except exc.DatabaseError:
        await callback.answer(text=text.DB_ERROR, show_alert=True)
    except ConnectionError:
        await callback.answer(text=text.YOO_ERROR, show_alert=True)
    finally:
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
