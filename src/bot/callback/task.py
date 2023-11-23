from aiogram.filters.callback_data import CallbackData


class ChooseCallbackFactory(CallbackData, prefix="choose"):
    value: str
