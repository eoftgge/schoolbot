import logging
import json
from typing import Dict

from aiogram.filters import Command
from aiohttp import ClientSession
from bs4 import BeautifulSoup

from aiogram import types, Router

router = Router(name=__name__)
logger = logging.getLogger(__name__)

URL_SCHEDULE = "http://raspisanie.nikasoft.ru"
URL_PARSE = URL_SCHEDULE + "/29406899.html#cls"


def strip_unnecessary(text: str) -> str:
    texts = text.split()
    return (" ".join(texts[texts.index("NIKA=") + 1:])).rstrip(";")


async def get_schedules(client: ClientSession) -> Dict:
    url: str

    async with client.get(URL_PARSE) as response:
        body = await response.text(encoding="utf-8")
        soup = BeautifulSoup(body, "html.parser")
        url_to_script = soup.find("script").attrs.get("src")
        assert url_to_script is not None
        url = URL_SCHEDULE + url_to_script

    async with client.get(url) as response:
        body = await response.text(encoding="utf-8")
        return json.loads(strip_unnecessary(body))


@router.message(Command("расписание", "расписания", "schedule"))
async def schedule(msg: types.Message):
    client = ClientSession()

    try:
        schedules = await get_schedules(client)
        default_class = schedules["CLASSES"]["029"]

        print(json.dumps(schedules, indent=4, ensure_ascii=False))
    finally:
        await client.close()

    await msg.reply("TODO")
