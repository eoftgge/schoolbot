import asyncio
import logging

from aiogram import Bot, Dispatcher

from src.bot.handlers import include_routers
from src.config import Config, get_path_config
from src.skysmart.session import SkySmartSession

logging.basicConfig(level=logging.DEBUG)
PATH_CONFIG = "config.ini"


async def main():
    config = Config(get_path_config(PATH_CONFIG))
    session = await SkySmartSession.from_pair(config.user_config.to_pair())
    bot = Bot(token=config.telegram_config.token, parse_mode="HTML")
    dp = Dispatcher()

    include_routers(dp)
    await dp.start_polling(bot, session=session, config=config)


if __name__ == "__main__":
    asyncio.run(main())
