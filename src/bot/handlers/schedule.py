import json
import logging
from typing import Dict, Optional

from aiogram import Router, types
from aiogram.filters import Command
from aiohttp import ClientSession
from bs4 import BeautifulSoup

router = Router(name=__name__)
logger = logging.getLogger(__name__)

URL_SCHEDULE = "http://raspisanie.nikasoft.ru"
URL_PARSE = URL_SCHEDULE + "/40811550.html#cls"


def strip_unnecessary(text: str) -> str:
    texts = text.split()
    return (" ".join(texts[texts.index("NIKA=") + 1 :])).rstrip(";")


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


@router.message(Command("расписание", "расписания", "schedule", "р", "s"))
async def schedule(msg: types.Message):
    client = ClientSession()
    arg = "".join(msg.text.split()[1:])

    try:
        schedules = await get_schedules(client)
        classes = schedules["CLASSES"]
        need_key: Optional[str] = None
        for key, value in classes.items():
            if value != arg:
                continue
            need_key = key
            break

        await msg.reply(f"key {need_key}")
        print(json.dumps(schedules, indent=4, ensure_ascii=False))
        print(schedules["CLASS_SCHEDULE"]["27"][need_key])
    finally:
        await client.close()

    await msg.reply("TODO")
