import logging

from aiogram import Bot, F, Router
from aiogram.filters.command import Command
from aiogram.types import FSInputFile, Message
from aiogram.fsm.context import FSMContext

import text
from core import exceptions as exc
from core.config import settings
from db import utils
from states import AdminService
from pytils.numeral import get_plural


logger = logging.getLogger()
router = Router()


@router.message(Command("admin"))
async def admin_actions(message: Message):
    try:
        user_data = await utils.get_user(message.from_user.id)
        if user_data.admin[0]:
            await message.answer("Ты админ! (Крутяк)")
        else:
            await message.answer(
                "Данный функционал предназначен для пользования администратором. Если вы администратор, а мы не знаем об этом, отправьте боту секретный пароль."
            )
    except exc.DatabaseError:
        await message.answer(text.DB_ERROR)


@router.message(F.text == settings.ADMIN_PASS.get_secret_value())
async def become_an_admin(message: Message, bot: Bot):
    try:
        await utils.set_admin(message.from_user.id)
    except exc.DatabaseError:
        await message.answer(text.DB_ERROR)
    else:
        await message.answer("Вы успешно зарегистрированы как администратор!")
    finally:
        await bot.delete_message(message.from_user.id, message.message_id)


@router.message(Command("dump"))
async def get_dump(message: Message):
    try:
        user_data = await utils.get_user(message.from_user.id)
        if user_data.admin[0]:
            dump = await utils.async_dump()
            await message.answer_document(FSInputFile(dump))
        else:
            await message.answer(
                "Данный функционал предназначен для пользования администратором. Если вы администратор, а мы не знаем об этом, отправьте боту секретный пароль."
            )
    except exc.DumpError as e:
        await message.answer(e.args[0])
    except exc.DatabaseError:
        await message.answer(text.DB_ERROR)


@router.message(Command("send"))
async def admin_mailing_start(message: Message, state: FSMContext):
    try:
        user_data = await utils.get_user(message.from_user.id)
        if user_data.admin[0]:
            await state.set_state(AdminService.mailing_confirm)
            await message.answer(
                "Введите сообщение для рассылки зарегистрированным пользователям"
            )
        else:
            await message.answer(
                "Данный функционал предназначен для пользования администратором. Если вы администратор, а мы не знаем об этом, отправьте боту секретный пароль."
            )
    except exc.DatabaseError:
        await message.answer(text.DB_ERROR)


@router.message(AdminService.mailing_confirm, F.text)
async def admin_mailing_confirm(message: Message, state: FSMContext):
    try:
        user_data = await utils.get_user(message.from_user.id)
        if user_data.admin[0]:
            await state.set_state(AdminService.mailing_message)
            await message.answer(f"Сообщение для рассылки:\n<b>{message.text}</b>")
            await message.answer(
                "Вы уверены, что хотите отправить это <b>ВСЕМ</b> пользователям?"
            )
            await state.update_data({"mailing_message": message.text})

        else:
            await message.answer(
                "Данный функционал предназначен для пользования администратором. Если вы администратор, а мы не знаем об этом, отправьте боту секретный пароль."
            )
    except exc.DatabaseError:
        await message.answer(text.DB_ERROR)


@router.message(AdminService.mailing_message, F.text.lower().in_(text.yes))
async def admin_mailing_finish(message: Message, bot: Bot, state: FSMContext):
    try:
        user_data = await utils.get_user(message.from_user.id)
        if user_data.admin[0]:
            mailing_message = (await state.get_data())["mailing_message"]

            all_users_data = await utils.get_all_users(message.from_user.id)

            for i, user_data in all_users_data.iterrows():
                await bot.send_message(user_data.telegram_id, mailing_message)
            await message.answer(
                f"Сообщение отправлено {get_plural(len(all_users_data), 'пользователю, пользователям, пользователям')}"
            )

        else:
            await message.answer(
                "Данный функционал предназначен для пользования администратором. Если вы администратор, а мы не знаем об этом, отправьте боту секретный пароль."
            )

        await state.clear()
        await state.set_state()

    except exc.DatabaseError:
        await message.answer(text.DB_ERROR)


@router.message(AdminService.mailing_message, F.text.lower().in_(text.no))
async def admin_mailing_cancel(message: Message, bot: Bot, state: FSMContext):
    await message.answer("Отменено")

    await state.clear()
    await state.set_state()
