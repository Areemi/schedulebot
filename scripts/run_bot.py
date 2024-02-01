import asyncio
import logging
import os

from aiogram import Bot, Dispatcher

from schedulebot.bot_configs import load_configs
from schedulebot.handlers import command_handlers, reply_handlers
from schedulebot.services.menu import set_main_menu

CURRENT_DPATH = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(CURRENT_DPATH, os.pardir))
DATA_DPATH = os.path.join(PROJECT_ROOT, "data")
CONFIG_DPATH = os.path.join(PROJECT_ROOT, "configs")
schedule_path = os.path.join(DATA_DPATH, 'timetable')
xlsx_path = os.path.join(schedule_path, 'schedule.xlsx')

logging.basicConfig(level=logging.INFO)


# @dp.message_handler(commands=['generate_timetable'])
# async def send_generate_timetable(message: types.Message):

#     """This handler will be called when user sends `/generate_timetable` command"""

#     schedule_path = os.path.join(DATA_DPATH, 'timetable')
#     xlsx_path = os.path.join(schedule_path, 'schedule.xlsx')
#     bool = os.path.isfile(xlsx_path)
#     if bool is False:
#         get_schedule()
#     await message.reply("file ready")
#     await message.answer("Вам нужен xlsx файл с расписанием?", reply_markup=kb)


# @dp.message_handler(filters.Text(equals="Да"))
# async def send_file(message: types.Message):

#     """This handler will be called when user sends `/send` command"""

#     with open(xlsx_path, "rb") as file:
#         await message.reply_document(file)


async def main():
    cfg = load_configs()

    bot = Bot(cfg.bot.token)
    dp = Dispatcher()

    dp.include_router(command_handlers.router)
    dp.include_router(reply_handlers.router)

    # NOTE: skip updates and run polling
    await bot.delete_webhook(drop_pending_updates=True)

    dp.startup.register(set_main_menu)
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())
