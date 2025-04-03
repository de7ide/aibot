import asyncio
import logging
from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommandScopeChat, BotCommandScopeDefault
from aiogram.enums import ParseMode

from database.engine import session_maker, create_db
from config_data import load_config, Config
from commands import USER_COMMANDS, ADMIN_COMMANDS
from handlers.user import user_router
from handlers.admin import admin_router
from middleware.db import DatabaseMiddleware


logger = logging.getLogger(__name__)

logging.basicConfig(
        level=logging.INFO,
        format='%(filename)s:%(lineno)d #%(levelname)-8s '
               '[%(asctime)s] - %(name)s - %(message)s')

config: Config = load_config()



bot = Bot(
    token=config.tg_bot.token,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

dp = Dispatcher()


async def set_bot_commands():
    await bot.set_my_commands(USER_COMMANDS, scope=BotCommandScopeDefault())

    for admin_id in config.tg_bot.admin_ids:
        await bot.set_my_commands(ADMIN_COMMANDS, scope=BotCommandScopeChat(chat_id=admin_id))


async def main():
    # logging.basicConfig(
    #     level=logging.INFO,
    #     format='%(filename)s:%(lineno)d #%(levelname)-8s '
    #            '[%(asctime)s] - %(name)s - %(message)s')

    # config: Config = load_config()

    await create_db()

    # bot = Bot(
    #     token=config.tg_bot.token,
    #     default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    # )

    # dp = Dispatcher()

    await bot.delete_webhook(drop_pending_updates=True)
    await set_bot_commands()
    dp.update.middleware(DatabaseMiddleware(session=session_maker))
    dp.include_router(admin_router)
    dp.include_router(user_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
