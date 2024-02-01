from aiogram import Router
from aiogram.filters import Text
from aiogram.types import Message

from ..lexicon.ru_lexicon import RU_LEXICON

router: Router = Router()


@router.message(Text(text=RU_LEXICON["yes"]))
async def process_yes_answer(message: Message):
    await message.answer(text=RU_LEXICON["yes_reply"])
    # TODO: send xlsx-file with timetable


@router.message(Text(text=RU_LEXICON["no"]))
async def process_no_answer(message: Message):
    await message.answer(text=RU_LEXICON["no_reply"])
