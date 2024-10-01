import logging
from contextlib import suppress
from datetime import datetime, timezone
from typing import Union
from uuid import uuid4

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram.utils.markdown import hlink
from pytils.numeral import get_plural
from requests.exceptions import ConnectionError
from yoomoney import Client, Quickpay

import text
from core import exceptions as exc
from core.config import settings
from core.metric import async_speed_metric
from db import utils
from kb import get_pay_keyboard, static_reg_button
from states import Service

logger = logging.getLogger()
router = Router()


# This function manages the subscription process for users.
@router.message(Command("sub"))
@router.callback_query(F.data == "user_payment")
@router.message(F.text == "Подписка")
@async_speed_metric
async def subscribe_manager(trigger: Union[Message, CallbackQuery], state: FSMContext):
    try:
        # Retrieve user data from the database
        user_data = await utils.get_user(trigger.from_user.id)

        if user_data is None:
            # If user data is not found, prompt registration
            await getattr(trigger, "message", trigger).answer(
                "Отсутсвуют данные пользователя. Зарегистрируйтесь",
                reply_markup=static_reg_button,
            )
            return
    except exc.DatabaseError:
        # Handle database errors
        await trigger.answer(text=text.DB_ERROR, show_alert=True)
    else:
        # Get the subscription status for the user
        sub_status = text.get_sub_status(user_data)

        if sub_status:
            # Set the state for subscription management
            await state.set_state(Service.sub)
            await state.update_data({"sub": {"month": 1, "stage": 1}})

            # Send subscription details to the user
            await getattr(trigger, "message", trigger).answer(
                "\n".join(
                    (
                        f"Ваша подписка: <b>{sub_status}</b>",
                        f"Актуальная стоимость 1 уровня подписки за 1 месяц: <b>{get_plural(settings.cost, 'рубль, рубля, рублей')}</b>",
                        f"Допустимое количество создаваемых конфигураций (подключаемых устройств) на 1 уровень подписки: <b>{settings.acceptable_config}</b>",
                        "(Одна конфигурация может быть подключена к нескольким устройствам, однако такие подключения не могут быть одновременными, поэтому рекомендуется создавать по одной конфигурации на каждое устройство)",
                        "<b>Плата взимается единоразово</b>",
                    )
                )
            )
            # Prompt the user to select a subscription level
            await getattr(trigger, "message", trigger).answer(
                f"""Выберите уровень подписки
Текущий:
    1 месяц
    1 уровень
Итоговая стоимость = <b>{get_plural(settings.cost*settings.transfer_fee, 'рубль, рубля, рублей')}</b>""",
                reply_markup=get_pay_keyboard(month=1, stage=1),
            )

        else:
            # Notify the user if the account has been deleted
            await getattr(trigger, "message", trigger).answer("Аккаунт удален")


# This function handles changes to the subscription stage or month.
@router.callback_query(F.data.startswith("stage_"))
@router.callback_query(F.data.startswith("month_"))
@async_speed_metric
async def edit_sub_stage(callback: CallbackQuery, bot: Bot, state: FSMContext):
    try:
        # Retrieve current subscription parameters from state
        user_sub_param = (await state.get_data())["sub"]
    except KeyError:
        # Handle expired message errors
        await callback.answer("Истек срок давности сообщения")
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
    else:
        # Update subscription parameters based on user input
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


# This function updates the displayed subscription stage and month.
@async_speed_metric
async def update_stage_text(message: Message, user_sub_param: dict):
    new_val_month = user_sub_param["month"]
    new_val_stage = user_sub_param["stage"]
    # Calculate the total cost based on subscription parameters
    SUM = settings.cost * new_val_stage * new_val_month * settings.transfer_fee

    with suppress(TelegramBadRequest):
        # Edit the message to show updated subscription details
        await message.edit_text(
            f"""Выберите уровень подписки
Текущий:
    {get_plural(new_val_month,'месяц, месяца, месяцев')}
    {get_plural(new_val_stage, 'уровень, уровня, уровней')}
Итоговая стоимость = <b>{get_plural(SUM, 'рубль, рубля, рублей')}</b>""",
            reply_markup=get_pay_keyboard(month=new_val_month, stage=new_val_stage),
        )


# This function handles the payment process for the subscription.
@router.callback_query(F.data == "pay_sub")
@async_speed_metric
async def pay(callback: CallbackQuery, bot: Bot, state: FSMContext):
    try:
        # Retrieve subscription details from state
        user_sub = (await state.get_data())["sub"]
        user_month = user_sub["month"]
        user_stage = user_sub["stage"]
        client = Client(settings.YOO_TOKEN.get_secret_value())
        transaction_label = uuid4()

        # Calculate the total payment amount
        SUM = settings.cost * user_stage * user_month * settings.transfer_fee

        # Create a Quickpay instance for payment processing
        quickpay = Quickpay(
            receiver=client.account_info().account,
            quickpay_form="shop",
            targets=f"Sponsor this project ({user_month} month | {user_stage} stage)",
            paymentType="SB",
            sum=SUM,
            label=transaction_label,
        )

        # Insert transaction details into the database
        await utils.insert_transaction(
            dict(
                user_id=callback.from_user.id,
                date=datetime.now(timezone.utc),
                amount=SUM,
                label=transaction_label,
                transaction_stage=user_stage,
                transaction_month=user_month,
                transaction_reference=quickpay.base_url,
            )
        )

        # Send payment links to the user
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
        # Clear the state after payment
        await state.clear()
        await state.set_state()

    except KeyError:
        # Handle expired message errors
        await callback.answer("Истек срок давности сообщения")
    except exc.DatabaseError:
        # Handle database errors
        await callback.answer(text=text.DB_ERROR, show_alert=True)
    except ConnectionError:
        # Handle connection errors
        await callback.answer(text=text.YOO_ERROR, show_alert=True)
    finally:
        # Delete the original message after processing
        await bot.delete_message(callback.from_user.id, callback.message.message_id)
