import math
from enum import Enum
from typing import Optional, Union, Sequence

from aiogram.types import ReplyKeyboardMarkup, KeyboardButtonRequestChat, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData

from config_reader import config
from database.models import Chat


class SettingType(str, Enum):
    members_count = "members_count"
    arab_filter_flag = "arab_filter_flag"
    delete_request = "delete_request"
    delete_submit = "delete_submit"
    delete_cancel = "delete_cancel"


class ChatSettingsCbData(CallbackData, prefix="chat_settings"):
    chat_id: int
    setting_type: SettingType
    value: Optional[Union[int, bool]] = None


def get_start_menu() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()

    kb.button(text="💬 Мои чаты")
    kb.button(
        text="⚙️ Добавить чат",
        request_chat=KeyboardButtonRequestChat(
            request_id=1,
            chat_is_channel=False,
            request_title=True,
            request_username=True
        )
    )
    kb.button(text="✏️ Дефолтное сообщение")

    kb.adjust(2, 1)
    return kb.as_markup(resize_keyboard=True)


def get_chat_settings_menu(chat_id: int, current_arab_filter_flag: bool = True) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.button(text="-10 👤", callback_data=ChatSettingsCbData(
        chat_id=chat_id,
        setting_type=SettingType.members_count,
        value=-10
    ))
    kb.button(text="+10 👤", callback_data=ChatSettingsCbData(
        chat_id=chat_id,
        setting_type=SettingType.members_count,
        value=10
    ))

    if current_arab_filter_flag:
        kb.button(
            text="👳🏾 Выключить фильтр чурок",
            callback_data=ChatSettingsCbData(
                chat_id=chat_id,
                setting_type=SettingType.arab_filter_flag,
                value=False
            )
        )

    else:
        kb.button(
            text="👳🏾 Включить фильтр чурок",
            callback_data=ChatSettingsCbData(
                chat_id=chat_id,
                setting_type=SettingType.arab_filter_flag,
                value=True
            )
        )

    kb.button(text="🗑 Удалить", callback_data=ChatSettingsCbData(
        chat_id=chat_id,
        setting_type=SettingType.delete_request
    ))

    kb.adjust(2, 1, 1)

    return kb.as_markup()


def get_delete_request_menu(chat_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Подтведить", callback_data=ChatSettingsCbData(
        chat_id=chat_id,
        setting_type=SettingType.delete_submit
    ))
    kb.button(text="Отменить", callback_data=ChatSettingsCbData(
        chat_id=chat_id,
        setting_type=SettingType.delete_cancel
    ))

    kb.adjust(2)

    return kb.as_markup()


def get_cancel_menu() -> ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="⬅️ Отменить")

    return kb.as_markup(resize_keyboard=True)


class ChatInfoCbData(CallbackData, prefix="chat_info"):
    chat_id: int


class PaginationCbData(CallbackData, prefix="pagination"):
    page: int


async def get_all_chats_menu(chats: Sequence[Chat], page: int = 0) -> InlineKeyboardMarkup:
    limit = config.page_limit
    start_offset = page * limit
    end_offset = start_offset + limit
    index = 1

    kb = InlineKeyboardBuilder()

    for chat in chats[start_offset:end_offset]:
        kb.row(InlineKeyboardButton(
            text=f"{start_offset + index}. {chat.title}",
            callback_data=ChatInfoCbData(chat_id=chat.id).pack()
        ))
        index += 1

    pages_count = math.ceil(len(chats) / limit)
    previous_page = (page - 1) if page > 0 else pages_count - 1
    next_page = (page + 1) if end_offset < len(chats) else 0

    pagination_buttons = [
        InlineKeyboardButton(text="⬅️", callback_data=PaginationCbData(page=previous_page).pack()),
        InlineKeyboardButton(text=f"{page+1}/{pages_count}", callback_data="none"),
        InlineKeyboardButton(text="➡️", callback_data=PaginationCbData(page=next_page).pack())
    ]

    kb.row(*pagination_buttons)

    return kb.as_markup()
