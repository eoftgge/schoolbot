import logging

import openai
from aiogram import Router, types
from aiogram.filters.command import Command, CommandObject

from src.bot.commands import GPT_COMMAND

router = Router(name=__name__)
logger = logging.getLogger(__name__)


@router.message(Command(GPT_COMMAND))
async def gpt(
    message: types.Message, gpt_client: openai.AsyncOpenAI, command: CommandObject
):
    if command.args is None:
        await message.reply("Пожалуйста, укажите текст (пример: `/gpt текст`)")
        return

    outbound_message = await message.reply("Подождите, пожалуйста...")
    try:
        completion = await gpt_client.chat.completions.create(
            messages=[{"role": "user", "content": command.args}],
            model="gpt-3.5-turbo",
        )
        await outbound_message.edit_text(text=completion.choices[0].message.content)
    except openai.PermissionDeniedError:
        await outbound_message.edit_text(
            "К сожалению, доступ к ChatGPT запрещен, поскольку бот находится на территории РФ"
        )
