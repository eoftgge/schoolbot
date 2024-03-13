import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from openai import AsyncOpenAI

from src.bot.handlers import include_routers
from src.config import Config, get_path_config
from src.skysmart.session import SkySmartSession

logging.basicConfig(level=logging.DEBUG)
PATH_CONFIG = "config.ini"


async def main():
    config = Config(get_path_config(PATH_CONFIG))
    sky_session = await SkySmartSession.from_pair(config.user_config.to_pair())
    gpt_client = AsyncOpenAI(api_key=config.gpt_config.token)
    bot = Bot(token=config.telegram_config.token, parse_mode=ParseMode.MARKDOWN.value)
    dp = Dispatcher()

    include_routers(dp)
    await dp.start_polling(
        bot, sky_session=sky_session, gpt_client=gpt_client, config=config
    )


if __name__ == "__main__":
    asyncio.run(main())
