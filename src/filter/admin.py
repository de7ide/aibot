from aiogram.filters import Filter
import os
from aiogram import Bot, types
from config_data.config import Config, load_config


class IsAdmin(Filter):
    def __init__(self) -> None:
        pass

    async def __call__(self, message: types.Message, config_usr: Config = load_config()) -> bool:
        return message.from_user.id in config_usr.tg_bot.admin_ids