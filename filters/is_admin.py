from aiogram.filters import BaseFilter
from aiogram.types import Message

from config_reader import config


class IsAdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id == config.admin_telegram_id
