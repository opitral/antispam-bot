import logging
from contextlib import suppress

from aiogram import Router, F, html
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Chat
from database.orm_queries import find_chat_by_telegram_id, add_chat, set_chat_title, find_chat_by_id, \
    set_chat_allowed_members, set_chat_arab_filter_flag, delete_chat, get_default_message_latest, add_default_message
from keyboards.admin import get_start_menu, get_chat_settings_menu, get_delete_request_menu, get_cancel_menu
from keyboards.admin import ChatSettingsCbData, SettingType
from filters.chat_type import ChatTypeFilter, IsAdminFilter

router = Router()
router.message.filter(ChatTypeFilter(is_group=False), IsAdminFilter())


def get_chat_info(chat: Chat):
    return (
        f"⭐️ ID: {chat.id}\n"
        f"📱 Telegram ID: {chat.telegram_id}\n"
        f"✏️ Название: {chat.title}\n"
        f"👥 Разрешено пользователей: {chat.allowed_members}\n"
        f"{'🟢' if chat.arab_filter_flag else '🔴'} Фильтр чурок: {'включен' if chat.arab_filter_flag else 'выключен'}\n"
        f"📅 Дата добавления: {chat.created_at.strftime('%Y-%m-%d %H:%M')}"
    )


@router.message(Command("start"))
async def command_start(message: Message):
    await message.answer(
        "👋 Здравствуйте, админ!",
        reply_markup=get_start_menu()
    )


@router.message(F.chat_shared)
async def add_group_to_white_list(message: Message, session: AsyncSession):
    chat_shared_telegram_id = str(message.chat_shared.chat_id)
    chat_shared_title = message.chat_shared.title

    found_chat = await find_chat_by_telegram_id(session, chat_shared_telegram_id)

    if found_chat:
        if found_chat.title != chat_shared_title:
            await set_chat_title(session, found_chat, chat_shared_title)
            await message.answer("Название чата обновлено")

        else:
            await message.answer("Этот чат уже добавлен")

    else:
        new_chat = await add_chat(session, chat_shared_telegram_id, chat_shared_title)

        await message.answer(
            text=get_chat_info(new_chat),
            reply_markup=get_chat_settings_menu(new_chat.id, bool(new_chat.arab_filter_flag))
        )


@router.message(F.text.lower().contains("мои чаты"))
async def get_white_list(message: Message, session: AsyncSession):
    await message.answer("В разработке")


@router.callback_query(ChatSettingsCbData.filter(F.setting_type == SettingType.members_count))
async def change_allowed_members(callback: CallbackQuery, callback_data: ChatSettingsCbData, session: AsyncSession):
    found_chat = await find_chat_by_id(session, callback_data.chat_id)

    if not found_chat:
        return await callback.answer("Чат не найден")

    new_allowed_members = found_chat.allowed_members + callback_data.value

    if new_allowed_members < 0:
        return await callback.answer("Установлено минимальное значение")

    elif new_allowed_members > 1000:
        return await callback.answer("Установлено максимальное значение")

    found_chat = await set_chat_allowed_members(session, found_chat, new_allowed_members)

    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            text=get_chat_info(found_chat),
            reply_markup=get_chat_settings_menu(found_chat.id, bool(found_chat.arab_filter_flag))
        )
    await callback.answer()


@router.callback_query(ChatSettingsCbData.filter(F.setting_type == SettingType.arab_filter_flag))
async def change_arab_filter_flag(callback: CallbackQuery, callback_data: ChatSettingsCbData, session: AsyncSession):
    found_chat = await find_chat_by_id(session, callback_data.chat_id)

    if not found_chat:
        return await callback.answer("Чат не найден")

    if found_chat.arab_filter_flag == callback_data.value:
        await callback.answer(f"Фильтр уже {'включен' if found_chat.arab_filter_flag else 'выключен'}")

    else:
        await set_chat_arab_filter_flag(session, found_chat, callback_data.value)

    await callback.message.edit_text(
        text=get_chat_info(found_chat),
        reply_markup=get_chat_settings_menu(found_chat.id, bool(found_chat.arab_filter_flag))
    )
    await callback.answer()


@router.callback_query(ChatSettingsCbData.filter(F.setting_type == SettingType.delete_request))
async def make_delete_request(callback: CallbackQuery, callback_data: ChatSettingsCbData, session: AsyncSession):
    found_chat = await find_chat_by_id(session, callback_data.chat_id)

    if not found_chat:
        return await callback.answer("Чат не найден")

    await callback.message.edit_text(
        text=f"Вы уверены, что хотите удалить чат {html.bold(html.quote(found_chat.title))}?",
        reply_markup=get_delete_request_menu(found_chat.id),
        parse_mode=ParseMode.HTML
    )


@router.callback_query(ChatSettingsCbData.filter(F.setting_type == SettingType.delete_submit))
async def make_delete_submit(callback: CallbackQuery, callback_data: ChatSettingsCbData, session: AsyncSession):
    found_chat = await find_chat_by_id(session, callback_data.chat_id)

    if not found_chat:
        return await callback.answer("Чат не найден")

    await delete_chat(session, found_chat)

    await callback.message.edit_text(
        text=f"Чат {html.bold(html.quote(found_chat.title))} удален",
        parse_mode=ParseMode.HTML
    )
    await callback.answer()


@router.callback_query(ChatSettingsCbData.filter(F.setting_type == SettingType.delete_cancel))
async def make_delete_cancel(callback: CallbackQuery, callback_data: ChatSettingsCbData, session: AsyncSession):
    found_chat = await find_chat_by_id(session, callback_data.chat_id)

    if not found_chat:
        return await callback.answer("Чат не найден")

    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            text=get_chat_info(found_chat),
            reply_markup=get_chat_settings_menu(found_chat.id, bool(found_chat.arab_filter_flag))
        )
    await callback.answer()


class SetDefaultMessage(StatesGroup):
    setting_new_default_message = State()


@router.message(F.text.lower().contains("дефолтное сообщение"))
async def set_default_message_request(message: Message, session: AsyncSession, state: FSMContext):
    latest_default_message = await get_default_message_latest(session)
    await message.answer(
        f"{html.bold('Текущее сообщение')}\n\n"
        f"{html.quote(latest_default_message.text) if latest_default_message else 'Не установлено'}",
        parse_mode=ParseMode.HTML
    )
    await message.answer(f"Отправьте мне новое сообщение", reply_markup=get_cancel_menu())
    await state.set_state(SetDefaultMessage.setting_new_default_message)


@router.message(SetDefaultMessage.setting_new_default_message, F.text.lower().contains("отменить"))
async def set_default_message_cancel(message: Message, state: FSMContext):
    await message.answer(text="Действие отменено", reply_markup=get_start_menu())
    await state.clear()


@router.message(SetDefaultMessage.setting_new_default_message, F.text)
async def set_default_message(message: Message, session: AsyncSession, state: FSMContext):
    await state.update_data(new_default_message_text=message.text.lower())
    admin_data = await state.get_data()

    await add_default_message(session, admin_data["new_default_message_text"])

    await message.answer("Новое дефолтное сообщение установлено", reply_markup=get_start_menu())
    await state.clear()


@router.message(SetDefaultMessage.setting_new_default_message)
async def set_default_message_unknown(message: Message, session: AsyncSession, state: FSMContext):
    await message.answer("Отправьте мне текстовое сообщение")


@router.message()
async def unknown_command(message: Message):
    await message.answer("Неизвестная команда", reply_markup=get_start_menu())
