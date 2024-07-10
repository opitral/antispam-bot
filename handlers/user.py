from aiogram import Router
from aiogram.types import Message

from filters.chat_type import ChatTypeFilter


router = Router()
router.message.filter(ChatTypeFilter(is_group=False))


@router.message()
async def default_answer(message: Message):
    await message.answer("Доброго дня, якщо ви хочете дізнатися більше про функціонал бота. Напишіть: @parlament_er")
