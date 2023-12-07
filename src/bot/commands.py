from aiogram import Bot
from aiogram.types import BotCommand

SCHEDULE_COMMAND = BotCommand(
    command="schedule", description="Get a schedules from school"
)
TASK_COMMAND = BotCommand(command="task", description="Get a solution")


async def setup_commands(bot: Bot):
    commands = [SCHEDULE_COMMAND, TASK_COMMAND]
    await bot.set_my_commands(
        commands=commands,
    )
