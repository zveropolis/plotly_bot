import logging
import os
from contextlib import suppress
from typing import Union

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.command import Command
from aiogram.types import CallbackQuery, FSInputFile, Message
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
        create_cfg_btn, create_output_cfg_btn = get_config_keyboard()

        if user_data.configs:
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
                        await getattr(trigger, "message", trigger).answer(
                            config_text, reply_markup=create_output_cfg_btn
                        )

        if user_data.active == UserActivity.active:
            cfg_number = get_plural(
                settings.acceptable_config[user_data.stage] - len(user_data.configs),
                "конфигурацию, конфигурации, конфигураций",
            )
            await getattr(trigger, "message", trigger).answer(
                f"Вы можете создать еще {cfg_number}", reply_markup=create_cfg_btn
            )
        elif user_data.active == UserActivity.inactive:
            await getattr(trigger, "message", trigger).answer(
                text.UNPAY, reply_markup=static_pay_button
            )


@router.message(Command("create"))
@router.callback_query(F.data == "create_configuration")
@async_speed_metric
async def create_config_data(trigger: Union[Message, CallbackQuery], bot: Bot):
    try:
        user_data: UserData = await find_user(trigger, configs=True)
        if not user_data:
            return
        elif user_data.active != UserActivity.active:
            raise exc.PayError

        elif len(user_data.configs) < settings.acceptable_config[user_data.stage]:
            wg = WgConfigMaker()
            conf = await wg.move_user(move="add", user_id=trigger.from_user.id)
            config: WgConfig = await utils.add_wg_config(
                conf, user_id=trigger.from_user.id
            )

        else:
            raise exc.StagePayError

    except exc.DatabaseError:
        await trigger.answer(text=text.DB_ERROR, show_alert=True)
    except exc.WireguardError:
        await trigger.answer(text=text.WG_ERROR, show_alert=True)
    except exc.StagePayError:
        await getattr(trigger, "message", trigger).answer(
            "Достигнуто максимальное количество конфигураций для данного тарифа.",
            reply_markup=static_pay_button,
        )
        await bot.delete_message(
            trigger.from_user.id, getattr(trigger, "message", trigger).message_id
        )
    except exc.PayError:
        await getattr(trigger, "message", trigger).answer(
            text.UNPAY, reply_markup=static_pay_button
        )
    else:
        create_cfg_btn, create_output_cfg_btn = get_config_keyboard()

        await trigger.answer(text="Конфигурация успешно создана", show_alert=True)
        await getattr(trigger, "message", trigger).answer(
            f"Конфигурация: {config.name} | id: {config.user_private_key[:4]}",
            reply_markup=create_output_cfg_btn,
        )

        with suppress(TelegramBadRequest):
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


@router.callback_query(F.data == "create_conf_text")
@async_speed_metric
async def get_config_text(callback: CallbackQuery):
    user_config: WgConfig = await find_config(callback)

    config = text.get_config_data(user_config)

    await callback.message.answer("Конфигурация " + callback.message.text)
    await callback.message.answer(f"<pre>{config}</pre>")


@router.callback_query(F.data == "create_conf_file")
@async_speed_metric
async def get_config_file(callback: CallbackQuery):
    user_config: WgConfig = await find_config(callback)

    config = text.get_config_data(user_config)
    config_file = await text.create_config_file(config)

    await callback.message.answer("Конфигурация " + callback.message.text)
    await callback.message.answer_document(
        FSInputFile(config_file, f"{user_config.name}.conf")
    )
    os.remove(config_file)


@router.callback_query(F.data == "create_conf_qr")
@async_speed_metric
async def get_config_qr(callback: CallbackQuery):
    user_config: WgConfig = await find_config(callback)

    config = text.get_config_data(user_config)
    config_qr = text.create_config_qr(config)

    await callback.message.answer("Конфигурация " + callback.message.text)
    await callback.message.answer_photo(
        FSInputFile(config_qr, f"{user_config.name}_wg.conf")
    )
    os.remove(config_qr)
