from aiogram import Router
from aiogram.types import Message

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import DefaultMessage
from filters.chat_type import ChatTypeFilter


router = Router()
router.message.filter(ChatTypeFilter(is_group=False))


@router.message()
async def default_answer(message: Message, session: AsyncSession):
    result = await session.execute(select(DefaultMessage).order_by(DefaultMessage.created_at.desc()).limit(1))
    latest_default_message = result.scalars().first()

    if latest_default_message:
        await message.answer(latest_default_message.text)
