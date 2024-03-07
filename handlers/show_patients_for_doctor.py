from aiogram import Router, F, Bot
from aiogram.types import Message

from database.db import show_doctor_surname
from keyboards import back_button
from utils import get_patients_info, create_text_report

router = Router()


@router.message(F.text == 'Покажи моих пациентов')
async def show_patients(message: Message):
    try:
        text = create_text_report(message)
        await message.answer(text, reply_markup=back_button)
    except Exception as e:
        await message.answer('Проверьте всем ли назначен лечащий врач')


async def show_patients_schedule(bot: Bot):
    pass
    # await bot.send_message(chat_id=, text=, disable_notification=True)