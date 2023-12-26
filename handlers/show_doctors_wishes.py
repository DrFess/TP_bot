from aiogram import Router, F
from aiogram.types import Message

from utils import get_wishes_data

router = Router()


@router.message(F.text == 'Показать пожелания врачей')
async def show_wishes(message: Message):
    data = get_wishes_data()
    await message.answer(f'Не ставить смены: {data[0]}')
    await message.answer(f'Ставить смены: {data[1]}')
