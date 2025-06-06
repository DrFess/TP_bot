from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command


from keyboards import back_button
from utils import create_text_report

router = Router()


@router.message(F.text == 'Покажи моих пациентов' or Command(commands=['my_patients']))
async def show_patients(message: Message):
    try:
        text = create_text_report(message.from_user.id)
        await message.answer(text, reply_markup=back_button)
    except Exception as e:
        await message.answer(f'{e}')
