from aiogram.types import ReplyKeyboardMarkup, KeyboardButtonRequestChat, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder, InlineKeyboardBuilder


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


def get_access_members_count_changer() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()

    kb.button(
        text="+10",
        callback_data="1"
    )
    kb.button(
        text="-10",
        callback_data="2"
    )
    kb.button(
        text="🗑 Удалить",
        callback_data="3"
    )

    kb.adjust(2)
    return kb.as_markup()