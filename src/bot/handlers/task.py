import logging

from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command

from src.skysmart.utils import get_task_code, get_str_result
from ..commands import TASK_COMMAND, TASK_CANCEL_COMMAND
from ..states.task import StateTask
from ...skysmart.session import SkySmartSession

router = Router(name=__name__)
logger = logging.getLogger(__name__)


@router.message(Command(TASK_COMMAND))
async def start_task(message: types.Message, state: FSMContext) -> None:
    await state.set_state(StateTask.STATE_CODE)
    await message.answer("Здравия желаю, путник! Укажите пожалуйста код задачи!")


@router.message(Command(TASK_CANCEL_COMMAND))
async def cancel_task(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer("Задача была отменена. И зачем вы меня вызвали то?")


@router.message(StateTask.STATE_CODE)
async def process_code(message: types.Message, state: FSMContext, session: SkySmartSession) -> None:
    code = get_task_code(message.text)
    exercise = await session.get_answer_xml_uuids(code)

    if not exercise.success:
        await message.reply("Неодобрительно.. Твой код задачи не является валидным. Попробуй ещё раз..")
        return

    outbound_message = await message.reply(
        "Хорошо! Принял твои данные в обработку, имейте совесть и подождите.."
    )
    result = await get_str_result(exercise, code, session)

    await outbound_message.edit_text(result)
    await state.clear()
