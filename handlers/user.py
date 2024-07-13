from aiogram import Router
from aiogram.types import Message
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries import get_default_message_latest
from filters.chat_type import ChatTypeFilter


router = Router()
router.message.filter(ChatTypeFilter(is_group=False))


@router.message()
async def default_answer(message: Message, session: AsyncSession):
    latest_default_message = await get_default_message_latest(session)

    if latest_default_message:
        await message.answer(latest_default_message.text)
