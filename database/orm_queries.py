from datetime import datetime, timedelta
from typing import Sequence, List

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from database.models import Chat, DefaultMessage, Member


async def find_chat_by_telegram_id(session: AsyncSession, telegram_id: str) -> Chat:
    query = select(Chat).where(Chat.telegram_id == telegram_id)
    result = await session.execute(query)
    found_chat = result.scalars().first()
    return found_chat


async def find_chat_by_id(session: AsyncSession, _id: int) -> Chat:
    query = select(Chat).where(Chat.id == _id)
    result = await session.execute(query)
    found_chat = result.scalars().first()
    return found_chat


async def add_chat(session: AsyncSession, telegram_id: str, title: str) -> Chat:
    chat = Chat(telegram_id=telegram_id, title=title)
    session.add(chat)
    await session.commit()
    return chat


async def set_chat_title(session: AsyncSession, chat: Chat, title: str) -> Chat:
    chat.title = title
    await session.commit()
    return chat


async def get_all_chats(session: AsyncSession) -> Sequence[Chat]:
    query = select(Chat).order_by(Chat.created_at.desc())
    result = await session.execute(query)
    all_chats = result.scalars().all()
    return all_chats


async def set_chat_allowed_members(session: AsyncSession, chat: Chat, allowed_members: int) -> Chat:
    chat.allowed_members = allowed_members
    await session.commit()
    return chat


async def set_chat_arab_filter_flag(session: AsyncSession, chat: Chat, arab_filter_flag: bool) -> Chat:
    chat.arab_filter_flag = arab_filter_flag
    await session.commit()
    return chat


async def delete_chat(session: AsyncSession, chat: Chat):
    await session.delete(chat)
    await session.commit()


async def get_default_message_latest(session: AsyncSession) -> DefaultMessage:
    query = select(DefaultMessage).order_by(DefaultMessage.created_at.desc()).limit(1)
    result = await session.execute(query)
    default_message = result.scalars().first()
    return default_message


async def add_default_message(session: AsyncSession, text: str) -> DefaultMessage:
    default_message = DefaultMessage(text=text)
    session.add(default_message)
    await session.commit()
    return default_message


async def add_member(
        session: AsyncSession,
        telegram_id: str,
        chat_id: int,
        username: str = None,
        first_name: str = None,
        last_name: str = None,
        is_premium: bool = None,
        status: str = None
) -> Member:
    member = Member(
        telegram_id=telegram_id,
        chat_id=chat_id,
        username=username,
        first_name=first_name,
        last_name=last_name,
        is_premium=is_premium,
        status=status
    )

    session.add(member)
    await session.commit()
    return member


async def set_member_status(session: AsyncSession, member: Member, status: str) -> Member:
    member.status = status
    await session.commit()
    return member


async def find_member_by_telegram_id_and_chat_id(session: AsyncSession, telegram_id: str, chat_id: int) -> Member:
    query = select(Member).where(Member.telegram_id == telegram_id, Member.chat_id == chat_id)
    result = await session.execute(query)
    member = result.scalars().first()
    return member


async def count_members(session: AsyncSession, chat_id: int, status: List[str]) -> int:
    today_start = datetime.combine(datetime.today(), datetime.min.time())
    tomorrow_start = today_start + timedelta(days=1)

    query = (
        select(func.count(Member.id))
        .where(
            Member.chat_id == chat_id,
            Member.status.in_(status),
            Member.updated_at >= today_start,
            Member.updated_at < tomorrow_start
        )
    )
    result = await session.execute(query)
    return result.scalar_one()
