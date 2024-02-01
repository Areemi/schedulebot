from aiogram.types import KeyboardButton
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from ..lexicon.ru_lexicon import RU_LEXICON

button_yes: KeyboardButton = KeyboardButton(text=RU_LEXICON["yes"])
button_no: KeyboardButton = KeyboardButton(text=RU_LEXICON["no"])

yes_no_kb_builder: ReplyKeyboardBuilder = ReplyKeyboardBuilder()
# Add buttons to keyboard builder
yes_no_kb_builder.row(button_yes, button_no, width=2)

yes_no_kb = yes_no_kb_builder.as_markup(one_time_keyboard=True, resize_keyboard=True)
