from aiogram import Router, F
from aiogram.types import Message

from database.db import show_doctor_surname
from keyboards import back_button
from utils import get_patients_info

router = Router()


@router.message(F.text == 'Покажи моих пациентов')
async def show_patients(message: Message):
    try:
        all_data = get_patients_info()
        doctor = show_doctor_surname(message.from_user.id)
        data_for_doctor = all_data.get(doctor)
        ward = 0
        text = ''
        for item in data_for_doctor:
            patient = item.split(' ')
            if ward != patient[0]:
                ward = patient[0]
                text += ward + '\n'
            patient_surname = patient[1]
            text += patient_surname + '\n'
            history_number = patient[2]
            text += history_number + '\n' + '----------\n'
        await message.answer(text, reply_markup=back_button)
    except Exception as e:
        await message.answer('Проверьте правильность заполнения полей таблицы')
