import logging

from aiogram import types, Router
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.filters import Command

from src.skysmart.parser.exercise import ExerciseParser
from src.skysmart.utils import get_task_code
from ...skysmart.models.xml import ExerciseMeta
from ...skysmart.session import SkySmartSession

router = Router(name=__name__)
logger = logging.getLogger(__name__)
cb_data = CallbackData(prefix="smart")


class StateTask(StatesGroup):
    state_code = State()
    state_info = State()


class ChooseCallbackFactory(CallbackData, prefix="choose"):
    value: str


@router.message(Command("задача", "task"))
async def handle_task(message: types.Message, state: FSMContext) -> None:
    texts = message.text.split()

    if len(texts) < 2:
        await message.answer("Вы мне не принесли аргументы! Я не готов терпеть такое отношение!")
        return

    match texts[1]:
        case "start" | "начать" | "старт":
            await start_task(message, state)
        case "cancel" | "отмена" | "стоп":
            await cancel_task(message, state)


@router.message(Command("ts"))
async def start_task(message: types.Message, state: FSMContext) -> None:
    await state.set_state(StateTask.state_code)
    await message.answer("Здравия желаю, путник! Укажите пожалуйста код задачи!")


@router.message(Command("tc"))
async def cancel_task(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer("Задача была отменена. И зачем вы меня вызвали то?")


@router.message(StateTask.state_code)
async def process_code(message: types.Message, state: FSMContext, session: SkySmartSession) -> None:
    code = get_task_code(message.text)
    exercise = await session.get_answer_xml_uuids(code)

    if not exercise.success:
        await message.reply("Неодобрительно.. Твой код задачи не является валидным. Попробуй ещё раз..")
        return

    outbound_message = await message.reply(
        "Хорошо! Принял твои данные в обработку, имейте совесть и подождите.."
    )
    result = await get_result(exercise, code, session)

    await outbound_message.edit_text(result)
    await state.clear()


async def get_result(
    exercise: ExerciseMeta,
    code: str,
    session: SkySmartSession
) -> str:
    parser = ExerciseParser(code, exercise)

    for uuid in exercise.meta.uuids:
        number = parser.increment_number()
        xml = await session.get_answer_xml(uuid, exercise)
        xml_parser = parser.get_xml_parser(xml)
        xml_parser.set_result(number)
        parser.push_ident()
        parser.push_result(xml_parser.get_result())

    return parser.get_result()
