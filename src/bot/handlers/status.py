from aiogram import Router, types
from aiogram.filters.command import Command

from src.bot.commands import STATUS_COMMAND

router = Router(name=__name__)


@router.message(Command(STATUS_COMMAND))
async def start(msg: types.Message):
    await msg.reply("Бот работает")
