import logging
from typing import Dict, Union

from aiogram import types, Router
from aiogram.filters.callback_data import CallbackData
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from ..utils.parser import ExerciseParser
from ..utils.utils import get_task_code
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


@router.message(commands=["task", "задача"])
async def handle_task(message: types.Message, state: FSMContext) -> None:
    texts = message.text.split()

    if len(texts) < 2:
        await message.answer("Вы мне принесли недостаточно аргументов! Я не готов терпеть такое отношение!")
        return

    match texts[1]:
        case "start" | "начать" | "старт":
            await start_task(message, state)
        case "cancel" | "отмена" | "стоп":
            await cancel_task(message, state)


@router.message(commands=["ts"])
async def start_task(message: types.Message, state: FSMContext) -> None:
    await state.set_state(StateTask.state_code)
    await message.answer("Здравия желаю, сэр/леди! Укажите пожалуйста код задачи!")


@router.message(commands=["tc"])
async def cancel_task(message: types.Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return

    await state.clear()
    await message.answer("Задача была отменена. И зачем вы меня вызвали без дела, то?")


@router.message(state=StateTask.state_code)
async def process_code(message: types.Message, state: FSMContext, session: SkySmartSession) -> None:
    code = get_task_code(message.text)
    exercise = await session.get_answer_xml_uuids(code)

    if not exercise.success:
        await message.answer("Неодобрительно.. Твой код задачи не является валидным. Попробуй ещё раз..")
        return

    builder = InlineKeyboardBuilder()
    builder.button(text="Да", callback_data=ChooseCallbackFactory(value="yes"))
    builder.button(text="Нет", callback_data=ChooseCallbackFactory(value="no"))

    await state.set_state(StateTask.state_info)
    await state.update_data(code=code)
    await state.update_data(exercise=exercise)
    await message.answer(
        "Весьма одобрительно, принял твой код задачи, теперь другой вопрос, путник.\n"
        "Желаете ли вы узнать дополнительную информацию по этой задаче?",
        reply_markup=builder.as_markup()
    )


@router.callback_query(ChooseCallbackFactory.filter(), state=StateTask.state_info)
async def process_info(
    callback_query: types.CallbackQuery,
    callback_data: ChooseCallbackFactory,
    state: FSMContext,
    session: SkySmartSession,
) -> None:
    await callback_query.message.delete()

    data = await state.update_data(is_info=callback_data.value == "yes")
    outbound_message = await callback_query.message.answer(
        "Хорошо! Принял твои данные в обработку, имейте совесть и подождите.."
    )
    result = await get_result(data, session)

    await outbound_message.edit_text(text=result)
    await callback_query.answer()
    await state.clear()


async def get_result(
    data: Dict[str, Union[str, bool, ExerciseMeta]],
    session: SkySmartSession
) -> str:
    exercise: ExerciseMeta = data.get("exercise")
    code: str = data.get("code")
    is_info: bool = data.get("is_info", False)
    parser = ExerciseParser(code, exercise)

    for uuid in exercise.meta.uuids:
        number = parser.increment_number()
        xml = await session.get_answer_xml(uuid, exercise)
        xml_parser = parser.get_xml_parser(xml)
        xml_parser.set_result(number)

        if is_info:
            xml_parser.push_ident().set_info_task(number)

        parser.push_result(xml_parser.get_result())

    if is_info:
        parser.push_ident().push_ident().set_info_room()

    return parser.get_result()
