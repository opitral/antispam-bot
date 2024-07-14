import re
from enum import Enum

from aiogram import Router, Bot
from aiogram.filters import ChatMemberUpdatedFilter, IS_NOT_MEMBER, IS_MEMBER, LEFT
from aiogram.types import ChatMemberUpdated
from sqlalchemy.ext.asyncio import AsyncSession

from database.orm_queries import find_chat_by_telegram_id, add_member, set_member_status, \
    find_member_by_telegram_id_and_chat_id, count_members
from filters.chat_type import ChatTypeFilter


router = Router()
router.message.filter(ChatTypeFilter(is_group=True))


class MemberStatus(Enum):
    JOIN = "join"
    LEAVE = "leave"
    BAN_BY_JOIN = "ban_by_join"
    BAN_BY_FILTER = "ban_by_filter"


def contains_arabic_or_chinese_symbol(text):
    arabic_range = re.compile(r'[\u0600-\u06FF]')
    chinese_range = re.compile(r'[\u4E00-\u9FFF]')

    contains_arabic = arabic_range.search(text) is not None
    contains_chinese = chinese_range.search(text) is not None

    return contains_arabic or contains_chinese


async def process_member_status(event: ChatMemberUpdated, session: AsyncSession, status: MemberStatus, bot: Bot = None):
    found_chat = await find_chat_by_telegram_id(session, str(event.chat.id))

    if not found_chat:
        return

    member = event.new_chat_member.user
    found_member = await find_member_by_telegram_id_and_chat_id(session, str(member.id), found_chat.id)

    if found_member:
        found_member = await set_member_status(session, found_member, status.value)

    else:
        found_member = await add_member(
            session,
            str(member.id),
            found_chat.id,
            member.username,
            member.first_name,
            member.last_name,
            True if member.is_premium else False,
            status=status.value
        )

    if status == MemberStatus.JOIN:
        joined_members = await count_members(session, found_chat.id, ["join", "ban_by_join", "ban_by_filter"])

        if joined_members >= found_chat.allowed_members:
            await bot.ban_chat_member(event.chat.id, member.id)
            await set_member_status(session, found_member, MemberStatus.BAN_BY_JOIN.value)

        elif found_chat.arab_filter_flag and contains_arabic_or_chinese_symbol(member.full_name):
            await bot.ban_chat_member(event.chat.id, member.id)
            await set_member_status(session, found_member, MemberStatus.BAN_BY_FILTER.value)


@router.chat_member(ChatMemberUpdatedFilter(IS_NOT_MEMBER >> IS_MEMBER))
async def on_user_join(event: ChatMemberUpdated, session: AsyncSession, bot: Bot):
    await process_member_status(event, session, MemberStatus.JOIN, bot)


@router.chat_member(ChatMemberUpdatedFilter(IS_MEMBER >> LEFT))
async def on_user_leave(event: ChatMemberUpdated, session: AsyncSession):
    await process_member_status(event, session, MemberStatus.LEAVE)
