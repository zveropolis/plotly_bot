import logging
import os
from contextlib import suppress
from typing import Union

from aiogram import Bot, F, Router
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters.command import Command
from aiogram.types import CallbackQuery, FSInputFile, Message
from pytils.numeral import get_plural
from random_word import RandomWords

import text
from core import exceptions as exc
from core.config import settings
from core.metric import async_speed_metric
from db import utils
from db.models import UserActivity, UserData, WgConfig
from kb import get_config_keyboard, static_pay_button, static_reg_button
from text import create_config_file, create_config_qr, get_config_data
from wg.utils import WgConfigMaker

logger = logging.getLogger()
router = Router()


@router.message(Command("me"))
@router.message(Command("config"))
@router.message(F.text.lower().in_(text.me))
@router.callback_query(F.data == "user_configurations")
@async_speed_metric
async def post_user_data(trigger: Union[Message, CallbackQuery], bot: Bot):
    try:
        user_data: UserData = await utils.get_user_with_configs(trigger.from_user.id)

        if user_data is None:
            await getattr(trigger, "message", trigger).answer(
                "Отсутсвуют данные пользователя. Зарегистрируйтесь",
                reply_markup=static_reg_button,
            )
            return
        elif user_data.active == UserActivity.deleted:
            await trigger.answer("Аккаунт удален", show_alert=True)
            return

    except exc.DatabaseError:
        await trigger.answer(text=text.DB_ERROR, show_alert=True)
    else:
        create_cfg_btn, create_output_cfg_btn = get_config_keyboard()

        if user_data.configs:
            await getattr(trigger, "message", trigger).answer("Ваши конфигурации:")

            for i, config in enumerate(user_data.configs, 1):
                if config.user_private_key:
                    await getattr(trigger, "message", trigger).answer(
                        f"({i}/{user_data.stage*settings.acceptable_config}) - Name: {config.name} | id: {config.user_private_key[:4]}",
                        reply_markup=create_output_cfg_btn,
                    )

        if user_data.active == UserActivity.active:
            cfg_number = get_plural(
                settings.acceptable_config * user_data.stage - len(user_data.configs),
                "конфигурацию, конфигурации, конфигураций",
            )
            await getattr(trigger, "message", trigger).answer(
                f"Вы можете создать еще {cfg_number}", reply_markup=create_cfg_btn
            )
        else:
            await getattr(trigger, "message", trigger).answer(
                text.UNPAY, reply_markup=static_pay_button
            )


@router.message(Command("create"))
@router.callback_query(F.data == "create_configuration")
@async_speed_metric
async def post_config_data(trigger: Union[Message, CallbackQuery], bot: Bot):
    try:
        user_data: UserData = await utils.get_user_with_configs(trigger.from_user.id)

        if user_data is None:
            await utils.add_user(trigger.from_user.id, trigger.from_user.full_name)
            raise exc.PayError
        elif user_data.active != UserActivity.active:
            raise exc.PayError

        elif len(user_data.configs) < user_data.stage * settings.acceptable_config:
            wg = WgConfigMaker()
            name_gen = RandomWords()
            conf = await wg.move_user(
                trigger.from_user.id, move="add", cfg_name=name_gen.get_random_word()
            )
            await utils.add_wg_config(conf, user_id=trigger.from_user.id)

        else:
            await getattr(trigger, "message", trigger).answer(
                "Достигнуто максимальное количество конфигураций. Повысьте уровень подписки, чтобы создать еще.",
                reply_markup=static_pay_button,
            )

            raise exc.StagePayError

    except exc.DatabaseError:
        await trigger.answer(text=text.DB_ERROR, show_alert=True)
    except exc.WireguardError:
        await trigger.answer(text=text.WG_ERROR, show_alert=True)
    except exc.StagePayError:
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
            f"Конфигурация: {conf['name']} | id: {conf['user_private_key'][:4]}",
            reply_markup=create_output_cfg_btn,
        )

        with suppress(TelegramBadRequest):
            cfg_number = get_plural(
                settings.acceptable_config * user_data.stage
                - len(user_data.configs)
                - 1,
                "конфигурацию, конфигурации, конфигураций",
            )
            await getattr(trigger, "message", trigger).edit_text(
                f"Вы можете создать еще {cfg_number}", reply_markup=create_cfg_btn
            )
    # finally:
    #     await bot.delete_message(
    #         trigger.from_user.id, getattr(trigger, "message", trigger).message_id
    #     )


@router.callback_query(F.data == "create_conf_text")
@async_speed_metric
async def get_config_text(callback: CallbackQuery):
    *_, cfg_id = callback.message.text.partition("| id: ")
    try:
        user_config = await utils.get_wg_config(callback.from_user.id, cfg_id)
    except exc.DatabaseError:
        await callback.answer(text=text.DB_ERROR, show_alert=True)
    else:
        config = get_config_data(user_config)

        await callback.message.answer("Конфигурация " + callback.message.text)
        await callback.message.answer(config)


@router.callback_query(F.data == "create_conf_file")
@async_speed_metric
async def get_config_file(callback: CallbackQuery):
    *_, cfg_id = callback.message.text.partition("| id: ")
    try:
        user_config: WgConfig = await utils.get_wg_config(callback.from_user.id, cfg_id)
    except exc.DatabaseError:
        await callback.answer(text=text.DB_ERROR, show_alert=True)
    else:
        config = get_config_data(user_config)
        config_file = await create_config_file(config)

        await callback.message.answer("Конфигурация " + callback.message.text)
        await callback.message.answer_document(
            FSInputFile(config_file, f"{user_config.name}_wg.conf")
        )
        os.remove(config_file)


@router.callback_query(F.data == "create_conf_qr")
@async_speed_metric
async def get_config_qr(callback: CallbackQuery):
    *_, cfg_id = callback.message.text.partition("| id: ")
    try:
        user_config: WgConfig = await utils.get_wg_config(callback.from_user.id, cfg_id)
    except exc.DatabaseError:
        await callback.answer(text=text.DB_ERROR, show_alert=True)
    else:
        config = get_config_data(user_config)
        config_qr = create_config_qr(config)

        await callback.message.answer("Конфигурация " + callback.message.text)
        await callback.message.answer_photo(
            FSInputFile(config_qr, f"{user_config.name}_wg.conf")
        )
        os.remove(config_qr)
