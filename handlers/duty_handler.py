from aiogram import Router, F
from aiogram.types import Message, ReplyKeyboardMarkup

from keyboards import wishes_or_ban, moderator_menu, back_button
from settings import moders
from utils import clear_duty_schedule, set_restricted_cells

router = Router()


@router.message(F.text == 'График')
async def edit_duty_schedule(message: Message):
    if message.from_user.id in moders:
        await message.answer('Вам доступно расширенное редактирование графика', reply_markup=moderator_menu)
    else:
        await message.answer(
            'Вы хотите указать в какие дни ставить или не ставить дежурства?',
            reply_markup=wishes_or_ban
        )


@router.message(F.text == 'Очистить график')
async def clear_schedule(message: Message):
    clear_duty_schedule()
    await message.answer('График очищен',
                         reply_markup=ReplyKeyboardMarkup(keyboard=[back_button], resize_keyboard=True))


@router.message(F.text == 'Заполнить график пожеланиями врачей')
async def edit_duty_schedule_doctors_wishes(message: Message):
    set_restricted_cells()
