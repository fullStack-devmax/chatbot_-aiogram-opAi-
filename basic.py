import datetime
import asyncio
import logging
import sys

from aiogram import Bot, Dispatcher
from aiogram.types import BotCommand, BotCommandScopeDefault

from config import ALLOWED_USER_IDS, TELEGRAM_BOT_TOKEN

from database import init_db
from handlers.cmd_handlers import cmd_router
from handlers.msg_handlers import msg_router


async def main():
    await init_db()
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    dp = Dispatcher()

    default_commands = [
        BotCommand(command="start", description="Start the bot"),
        BotCommand(command="language", description="Change your language"),
    ]
    await bot.set_my_commands(default_commands, scope=BotCommandScopeDefault())

    for admin_id in ALLOWED_USER_IDS:
        await bot.set_my_commands(
            default_commands + [BotCommand(command="users", description="See all users and their requests")],
            scope={"type": "chat", "chat_id": admin_id}
        )

    dp.include_routers(cmd_router, msg_router)
    await dp.start_polling(bot)



if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Bot stop')