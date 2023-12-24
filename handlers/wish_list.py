from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards import select_day_week_or_day_number
from utils import open_data_file, write_doctors_ban_days

router = Router()


class Step(StatesGroup):
    first = State()
    second = State()
    third = State()


@router.message(F.text == 'Не ставить смены')
async def get_doctor_surname(message: Message, state: FSMContext):
    await state.set_state(Step.first)
    doctors = open_data_file('doctors_list.json')
    builder = InlineKeyboardBuilder()
    for doctor in doctors.keys():
        builder.add(InlineKeyboardButton(text=f'{doctors[doctor]}', callback_data=f'{doctors[doctor]}'))
    builder.adjust(1)
    await message.answer('Для кого из врачей указать нежелательные дни дежурств', reply_markup=builder.as_markup())


@router.callback_query(Step.first)
async def select_day_by_number_or_day_week(callback: CallbackQuery, state: FSMContext):
    await state.update_data(doctor=callback.data)
    await state.set_state(Step.second)
    await callback.message.answer(
        'Вы собираетесь указать конкретные числа или дни недели в которые НЕ нужно ставить смены?',
        reply_markup=select_day_week_or_day_number
    )


@router.callback_query(Step.second)
async def indicate_days(callback: CallbackQuery, state: FSMContext):
    await state.update_data(choice=callback.data)
    if callback.data == 'day_week':
        await callback.message.answer('Укажите через запятую в какие дни недели НЕ ставить дежурства. '
                                      'Если требуется очистить список дней, отправьте точку "."')
    else:
        await callback.message.answer('Укажите через запятую в какие числа месяца НЕ ставить дежурства. '
                                      'Если требуется очистить список дней, отправьте точку "."')
    await state.set_state(Step.third)


@router.message(Step.third)
async def making_changes_to_schedule(message: Message, state: FSMContext):
    data = await state.get_data()
    doctor = data['doctor']
    if message.text != '.':
        days = message.text.split(', ')
        if data['choice'] == 'number':
            write_doctors_ban_days(doctor=doctor, ban_day=days, choice='numbers')
            await message.answer(f'Для {doctor} указаны даты {message.text}')
        else:
            write_doctors_ban_days(doctor=doctor, ban_day=days, choice='days')
            await message.answer(f'Для {doctor} указаны дни недели {message.text}')
    else:
        if data['choice'] == 'number':
            write_doctors_ban_days(doctor=doctor, ban_day=[], choice='numbers')
            await message.answer(f'Для {doctor} список нежелательных для дежурств дат очищен')
        else:
            write_doctors_ban_days(doctor=doctor, ban_day=[], choice='days')
            await message.answer(f'Для {doctor} список нежелательных для дежурств дней недели очищен')
