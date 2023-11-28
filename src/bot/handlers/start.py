from aiogram import Router, types
from aiogram.filters.command import Command

HELLO_TEXT = (
    "Привет, <b>{}</b>!\nДля получения ответов на задачу нужно ввести команду (без кавычек): /task «ссылка»\n"
    "(И следовать дальнейшим инструкциям! (пожалуйста))"
)
router = Router(name=__name__)


@router.message(Command(commands=["start"]))
async def start(msg: types.Message):
    await msg.reply(HELLO_TEXT.format(msg.from_user.full_name))
