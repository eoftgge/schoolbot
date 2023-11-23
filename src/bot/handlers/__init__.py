from aiogram import Dispatcher

from .schedule import router as schedule_router
from .start import router as start_router
from .task import router as task_router


def include_routers(dp: Dispatcher):
    dp.include_router(task_router)
    dp.include_router(start_router)
    dp.include_router(schedule_router)
