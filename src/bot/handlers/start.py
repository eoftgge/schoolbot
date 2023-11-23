from aiogram import Router, types
from aiogram.filters.command import Command

HELLO_TEXT = (
    "Здравия желаю, <b>{}</b>!\nДля получение сие ответов нужно ввести команду: /task start "
    "(И следовать дальнейшим инструкциям, будьте вежливыми, сэр/леди!)"
)
router = Router(name=__name__)


@router.message(Command(commands=["start"]))
async def start(msg: types.Message):
    await msg.reply(HELLO_TEXT.format(msg.from_user.full_name))
