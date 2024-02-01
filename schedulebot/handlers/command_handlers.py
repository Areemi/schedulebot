from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message

from ..keyboards.keyboards import yes_no_kb
from ..lexicon.ru_lexicon import RU_LEXICON

router: Router = Router()


@router.message(CommandStart())
async def handle_start_command(message: Message):
    await message.answer(RU_LEXICON["/start"])


@router.message(Command(commands="help"))
async def handle_help_command(message: Message):
    await message.answer(RU_LEXICON["/help"])


@router.message(Command(commands="generate_timetable"))
async def handle_schedule_command(message: Message):
    await message.answer(RU_LEXICON["/generate_timetable"], reply_markup=yes_no_kb)
