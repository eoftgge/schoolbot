import logging

from aiogram import Router, types
from aiogram.filters import Command, CommandObject
from aiogram.fsm.context import FSMContext

from src.bot.commands import TASK_COMMAND
from src.skysmart.session import SkySmartSession
from src.skysmart.utils import get_str_result, get_task_code

router = Router(name=__name__)
logger = logging.getLogger(__name__)


@router.message(Command(TASK_COMMAND))
async def process_task(
    message: types.Message,
    state: FSMContext,
    session: SkySmartSession,
    command: CommandObject,
):
    if command.args is None:
        await message.answer("Пример команды (без кавычек): `/task ссылка`")
        return

    code = get_task_code(command.args)
    exercise = await session.get_answer_xml_uuids(code)

    if not exercise.success:
        await message.reply(
            "Неодобрительно... Твой код задачи не является валидным. Попробуй ещё раз с другим кодом задачи"
        )
        return

    outbound_message = await message.reply(
        "Хорошо! Принял твои данные в обработку, имейте совесть и подождите"
    )
    result = await get_str_result(exercise, code, session)

    await outbound_message.edit_text(result)
    await state.clear()
