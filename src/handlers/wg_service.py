import logging
import os
from contextlib import suppress
from typing import Union

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.command import Command
from aiogram.types import CallbackQuery, FSInputFile, Message
from asyncssh import SSHClientConnection
from pytils.numeral import get_plural

import text
from core import exceptions as exc
from core.config import settings
from core.metric import async_speed_metric
from db import utils
from db.models import FreezeSteps, UserActivity, UserData, WgConfig
from handlers.utils import find_config, find_user
from kb import get_config_keyboard, static_pay_button, why_freezed_button
from wg.utils import WgConfigMaker

logger = logging.getLogger()
router = Router()


# This function handles user commands related to their configurations.
@router.message(Command("me"))
@router.message(Command("config"))
@router.message(F.text.lower().in_(text.me))
@router.callback_query(F.data == "user_configurations")
@async_speed_metric
async def post_user_data(trigger: Union[Message, CallbackQuery]):
    user_data: UserData = await find_user(trigger, configs=True)
    if not user_data:
        return
    else:
        # Get keyboard buttons for creating configurations
        create_cfg_btn, create_output_cfg_btn = get_config_keyboard()

        if user_data.configs:
            # Notify user of their existing configurations
            await getattr(trigger, "message", trigger).answer("Ваши конфигурации:")

            user_data.configs.sort(key=lambda conf: conf.id)
            for i, config in enumerate(user_data.configs, 1):
                if config.user_private_key:
                    config_text = f"({i}/{settings.acceptable_config[user_data.stage]}) - Name: {config.name} | id: {config.user_private_key[:4]}"

                    if config.freeze != FreezeSteps.no:
                        config_text = f'🥶<b>FREEZED</b>❄️\n<span class="tg-spoiler">{config_text}</span>'

                        await getattr(trigger, "message", trigger).answer(
                            config_text, reply_markup=why_freezed_button
                        )
                    else:
                        # Display each configuration with its name and ID
                        await getattr(trigger, "message", trigger).answer(
                            config_text, reply_markup=create_output_cfg_btn
                        )

        if user_data.active == UserActivity.active:
            # Calculate how many more configurations the user can create
            cfg_number = get_plural(
                settings.acceptable_config[user_data.stage] - len(user_data.configs),
                "конфигурацию, конфигурации, конфигураций",
            )
            await getattr(trigger, "message", trigger).answer(
                f"Вы можете создать еще {cfg_number}", reply_markup=create_cfg_btn
            )
        elif user_data.active == UserActivity.inactive:
            # Notify user to pay if their account is inactive
            await getattr(trigger, "message", trigger).answer(
                text.UNPAY, reply_markup=static_pay_button
            )


# This function handles the creation of new configurations.
@router.message(Command("create"))
@router.callback_query(F.data == "create_configuration")
@async_speed_metric
async def create_config_data(
    trigger: Union[Message, CallbackQuery], bot: Bot, wg_connection: SSHClientConnection
):
    try:
        user_data: UserData = await find_user(trigger, configs=True)
        if not user_data:
            return
        elif user_data.active != UserActivity.active:
            # Raise error if user is not active
            raise exc.PayError

        elif len(user_data.configs) < settings.acceptable_config[user_data.stage]:
            # Create a new configuration if the limit is not reached
            wg = WgConfigMaker()
            conf = await wg.move_user(
                move="add",
                user_id=trigger.from_user.id,
                conn=wg_connection,
            )
            config: WgConfig = await utils.add_wg_config(
                conf, user_id=trigger.from_user.id
            )

        else:
            raise exc.StagePayError

    except exc.DatabaseError:
        # Handle database errors
        await trigger.answer(text=text.DB_ERROR, show_alert=True)
    except exc.WireguardError:
        # Handle Wireguard-related errors
        await trigger.answer(text=text.WG_ERROR, show_alert=True)
    except exc.StagePayError:
        # Notify user if the maximum number of configurations is reached
        await getattr(trigger, "message", trigger).answer(
            "Достигнуто максимальное количество конфигураций для данного тарифа.",
            reply_markup=static_pay_button,
        )
        # Delete the message if the stage payment error occurs
        await bot.delete_message(
            trigger.from_user.id, getattr(trigger, "message", trigger).message_id
        )
    except exc.PayError:
        # Notify user to pay if their account is inactive
        await getattr(trigger, "message", trigger).answer(
            text.UNPAY, reply_markup=static_pay_button
        )
    else:
        # Notify user of successful configuration creation
        create_cfg_btn, create_output_cfg_btn = get_config_keyboard()

        await trigger.answer(text="Конфигурация успешно создана", show_alert=True)
        await getattr(trigger, "message", trigger).answer(
            f"Конфигурация: {config.name} | id: {config.user_private_key[:4]}",
            reply_markup=create_output_cfg_btn,
        )

        with suppress(TelegramBadRequest):
            # Update the message to show how many more configurations can be created
            cfg_number = get_plural(
                settings.acceptable_config[user_data.stage]
                - len(user_data.configs)
                - 1,
                "конфигурацию, конфигурации, конфигураций",
            )
            await getattr(trigger, "message", trigger).edit_text(
                f"Вы можете создать еще {cfg_number}", reply_markup=create_cfg_btn
            )

        if cfg_number.startswith("0"):
            await bot.delete_message(
                trigger.from_user.id, getattr(trigger, "message", trigger).message_id
            )


# This function retrieves and sends the configuration text to the user.
@router.callback_query(F.data == "create_conf_text")
@async_speed_metric
async def get_config_text(callback: CallbackQuery):
    user_config: WgConfig = await find_config(callback)

    # Get the configuration data and send it to the user
    config = text.get_config_data(user_config)

    await callback.message.answer("Конфигурация " + callback.message.text)
    await callback.message.answer(config)


# This function retrieves and sends the configuration file to the user.
@router.callback_query(F.data == "create_conf_file")
@async_speed_metric
async def get_config_file(callback: CallbackQuery):
    user_config: WgConfig = await find_config(callback)

    # Get the configuration data and create a config file
    config = text.get_config_data(user_config)
    config_file = await text.create_config_file(config)

    # Send the configuration file to the user
    await callback.message.answer("Конфигурация " + callback.message.text)
    await callback.message.answer_document(
        FSInputFile(config_file, f"{user_config.name}_wg.conf")
    )
    # Remove the temporary config file
    os.remove(config_file)


# This function retrieves and sends the configuration QR code to the user.
@router.callback_query(F.data == "create_conf_qr")
@async_speed_metric
async def get_config_qr(callback: CallbackQuery):
    user_config: WgConfig = await find_config(callback)

    # Get the configuration data and create a QR code
    config = text.get_config_data(user_config)
    config_qr = text.create_config_qr(config)

    # Send the QR code to the user
    await callback.message.answer("Конфигурация " + callback.message.text)
    await callback.message.answer_photo(
        FSInputFile(config_qr, f"{user_config.name}_wg.conf")
    )
    # Remove the temporary QR code file
    os.remove(config_qr)
