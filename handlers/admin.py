from contextlib import suppress

from aiogram import Router, F, html
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Chat
from keyboards.admin import get_start_menu, get_chat_settings_menu, get_delete_request_menu
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
    new_chat = Chat(
        telegram_id=str(message.chat_shared.chat_id),
        title=message.chat_shared.title
    )

    result = await session.execute(select(Chat).where(Chat.telegram_id == new_chat.telegram_id))
    found_chat = result.scalars().first()

    if found_chat:
        if found_chat.title != new_chat.title:
            found_chat.title = new_chat.title
            await session.commit()
            await message.answer("Название чата обновлено")

        else:
            await message.answer("Этот чат уже добавлен")

    else:
        session.add(new_chat)
        await session.commit()

        await message.answer(
            text=get_chat_info(new_chat),
            reply_markup=get_chat_settings_menu(new_chat.id, bool(new_chat.arab_filter_flag))
        )


@router.message(F.text.lower().contains("мои чаты"))
async def get_white_list(message: Message, session: AsyncSession):
    await message.answer("В разработке")


@router.callback_query(ChatSettingsCbData.filter(F.setting_type == SettingType.members_count))
async def change_allowed_members(callback: CallbackQuery, callback_data: ChatSettingsCbData, session: AsyncSession):
    result = await session.execute(select(Chat).where(Chat.id == callback_data.chat_id))
    found_chat = result.scalars().first()

    if not found_chat:
        return await callback.answer("Чат не найден")

    new_allowed_members = found_chat.allowed_members + callback_data.value

    if new_allowed_members < 0:
        return await callback.answer("Установлено минимальное значение")

    elif new_allowed_members > 1000:
        return await callback.answer("Установлено максимальное значение")

    found_chat.allowed_members = new_allowed_members
    await session.commit()
    await session.refresh(found_chat)

    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            text=get_chat_info(found_chat),
            reply_markup=get_chat_settings_menu(found_chat.id, bool(found_chat.arab_filter_flag))
        )
    await callback.answer()


@router.callback_query(ChatSettingsCbData.filter(F.setting_type == SettingType.arab_filter_flag))
async def change_arab_filter_flag(callback: CallbackQuery, callback_data: ChatSettingsCbData, session: AsyncSession):
    result = await session.execute(select(Chat).where(Chat.id == callback_data.chat_id))
    found_chat = result.scalars().first()

    if not found_chat:
        return await callback.answer("Чат не найден")

    if found_chat.arab_filter_flag == callback_data.value:
        await callback.answer(f"Фильтр уже {'включен' if found_chat.arab_filter_flag else 'выключен'}")

    else:
        found_chat.arab_filter_flag = callback_data.value
        await session.commit()
        await session.refresh(found_chat)

    await callback.message.edit_text(
        text=get_chat_info(found_chat),
        reply_markup=get_chat_settings_menu(found_chat.id, bool(found_chat.arab_filter_flag))
    )
    await callback.answer()


@router.callback_query(ChatSettingsCbData.filter(F.setting_type == SettingType.delete_request))
async def make_delete_request(callback: CallbackQuery, callback_data: ChatSettingsCbData, session: AsyncSession):
    result = await session.execute(select(Chat).where(Chat.id == callback_data.chat_id))
    found_chat = result.scalars().first()

    if not found_chat:
        return await callback.answer("Чат не найден")

    await callback.message.edit_text(
        text=f"Вы уверены, что хотите удалить чат {html.bold(html.quote(found_chat.title))}?",
        reply_markup=get_delete_request_menu(found_chat.id),
        parse_mode=ParseMode.HTML
    )


@router.callback_query(ChatSettingsCbData.filter(F.setting_type == SettingType.delete_submit))
async def make_delete_submit(callback: CallbackQuery, callback_data: ChatSettingsCbData, session: AsyncSession):
    result = await session.execute(select(Chat).where(Chat.id == callback_data.chat_id))
    found_chat = result.scalars().first()

    if not found_chat:
        return await callback.answer("Чат не найден")

    await session.delete(found_chat)
    await session.commit()

    await callback.message.edit_text(
        text=f"Чат {html.bold(html.quote(found_chat.title))} удален",
        parse_mode=ParseMode.HTML
    )
    await callback.answer()


@router.callback_query(ChatSettingsCbData.filter(F.setting_type == SettingType.delete_cancel))
async def make_delete_cancel(callback: CallbackQuery, callback_data: ChatSettingsCbData, session: AsyncSession):
    result = await session.execute(select(Chat).where(Chat.id == callback_data.chat_id))
    found_chat = result.scalars().first()

    if not found_chat:
        return await callback.answer("Чат не найден")

    with suppress(TelegramBadRequest):
        await callback.message.edit_text(
            text=get_chat_info(found_chat),
            reply_markup=get_chat_settings_menu(found_chat.id, bool(found_chat.arab_filter_flag))
        )
    await callback.answer()


@router.message()
async def unknown_command(message: Message):
    await message.answer("Неизвестная команда", reply_markup=get_start_menu())
