import logging
import asyncio

from aiogram import Bot, Dispatcher

from src.config import Config, get_path_config
from src.bot.handlers import include_routers
from src.skysmart.utils import create_session

logging.basicConfig(level=logging.INFO)
PATH_CONFIG = "config.ini"


async def main():
    config = Config(get_path_config(PATH_CONFIG))
    session = await create_session(config)
    bot = Bot(token=config.telegram_config.token, parse_mode="HTML")
    dp = Dispatcher()

    include_routers(dp)
    await dp.start_polling(bot, session=session, config=config)


if __name__ == "__main__":
    asyncio.run(main())
