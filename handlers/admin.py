import logging

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove

from keyboards.admin import get_start_menu, get_access_members_count_changer
from filters.chat_type import ChatTypeFilter
from filters.is_admin import IsAdminFilter

router = Router()
router.message.filter(ChatTypeFilter(is_group=False), IsAdminFilter())


@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Здравствуйте, админ!",
        reply_markup=get_start_menu()
    )


@router.message(F.chat_shared)
async def on_user_shared(message: Message):
    logging.info(message.chat_shared)
    await message.answer(
        text="⭐️ ID: 1\n📱 Telegram ID: 123456789\n✏️ Название: test title\n👥 Разрешено пользователей: 200\n📅 Дата добавления: 2024-07-10 15:47",
        reply_markup=get_access_members_count_changer()
    )


@router.message(F.text.lower().contains("мои чаты"))
async def get_my_chats(message: Message):
    await message.answer("your chats")
