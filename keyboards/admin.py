from enum import Enum
from typing import Optional, Union

from aiogram.types import ReplyKeyboardMarkup, KeyboardButtonRequestChat, InlineKeyboardMarkup
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder
from aiogram.filters.callback_data import CallbackData


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

    kb.adjust(2)
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
