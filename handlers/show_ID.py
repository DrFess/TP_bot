from aiogram import Router, F
from aiogram.types import Message

from keyboards import back_button

router = Router()


@router.message(F.text == 'Показать мой ID')
async def show_user_id(message: Message):
    await message.answer(f'Ваш ID {message.from_user.id}', reply_markup=back_button)
