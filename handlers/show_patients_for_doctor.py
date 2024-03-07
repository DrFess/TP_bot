from aiogram import Router, F, Bot
from aiogram.types import Message

from database.db import show_doctor_surname, show_all_doctors, get_doctor_telegram_id_by_surname
from keyboards import back_button
from utils import get_patients_info, create_text_report

router = Router()


@router.message(F.text == 'Покажи моих пациентов')
async def show_patients(message: Message):
    try:
        text = create_text_report(message.from_user.id)
        await message.answer(text, reply_markup=back_button)
    except Exception as e:
        await message.answer('Проверьте всем ли назначен лечащий врач')


async def show_patients_schedule(bot: Bot):
    all_patients = get_patients_info()
    for doctor in all_patients.keys():
        telegram_id = get_doctor_telegram_id_by_surname(doctor)
        text = create_text_report(telegram_id)
        await bot.send_message(chat_id=telegram_id, text=text, disable_notification=True)