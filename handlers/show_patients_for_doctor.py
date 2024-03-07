from aiogram import Router, F
from aiogram.types import Message

from bot import bot
from keyboards import back_button
from utils import create_text_report

router = Router()


@router.message(F.text == 'Покажи моих пациентов')
async def show_patients(message: Message):
    try:
        text = create_text_report(message.from_user.id)
        await message.answer(text, reply_markup=back_button)
    except Exception as e:
        await message.answer('Проверьте всем ли назначен лечащий врач')


@router.message(F.from_user.id == 7163899081)
async def test_message(message: Message):
    await bot.send_message(chat_id=233759537, text=message, disable_notification=True)
