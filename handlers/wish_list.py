from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db import show_all_doctors, add_wish_date, show_all_doctors_id
from keyboards import select_day_week_or_day_number, back_button
from settings import moders
from utils import open_data_file, write_doctors_wishes, create_date

router = Router()


class StepBans(StatesGroup):
    first = State()
    second = State()
    third = State()


class StepWishes(StatesGroup):
    first = State()
    second = State()
    third = State()


@router.message(F.text == 'Не ставить смены')
async def get_doctor_surname(message: Message, state: FSMContext):
    if message.from_user.id in moders:
        await state.set_state(StepBans.first)
        doctors = show_all_doctors()
        builder = InlineKeyboardBuilder()
        for doc in doctors:
            builder.row(
                InlineKeyboardButton(text=f"{doctors.get(doc)['фамилия']} {doctors.get(doc)['имя']}", callback_data=f'{doc}'))
        builder.adjust(1)
        await message.answer('Для кого из врачей указать НЕжелательные даты дежурств', reply_markup=builder.as_markup())
    elif message.from_user.id in show_all_doctors_id():
        await state.update_data(doctor=message.from_user.id)
        await state.set_state(StepBans.second)
        await message.answer('Отправьте, через запятую, числа в которые не нужно ставить дежурства без указания месяца.'
                             ' Например: 1, 2, 3, 4, 5 и т.п.')
    else:
        await message.answer('Вы не зарегистрированы в базе данных')


@router.callback_query(StepBans.first)
async def send_number_days(callback: CallbackQuery, state: FSMContext):
    await state.update_data(doctor=callback.data)
    await state.set_state(StepBans.second)
    await callback.message.answer('Отправьте, через запятую, числа в которые не нужно ставить дежурства '
                                  'без указания месяца. Например: 1, 2, 3, 4, 5 и т.п.')


@router.message(StepBans.second)
async def write_ban_days(message: Message, state: FSMContext):
    data = await state.get_data()
    for item in message.text.split(', '):
        date = create_date(item)
        add_wish_date(data['doctor'], date, False)
    await message.answer('Даты добавлены в НЕжелательные')
    await state.clear()



#
# @router.message(StepBans.third)
# async def making_changes_to_schedule(message: Message, state: FSMContext):
#     data = await state.get_data()
#     doctor = data['doctor']
#     if message.text != '.':
#         days = message.text.split(', ')
#         if data['choice'] == 'number':
#             write_doctors_wishes(doctor=doctor, ban_day=days, choice='numbers', file_name='wish_days')
#             await message.answer(f'Для {doctor} указаны даты {message.text}')
#         else:
#             write_doctors_wishes(doctor=doctor, ban_day=days, choice='numbers', file_name='wish_days')
#             await message.answer(f'Для {doctor} указаны дни недели {message.text}')
#     else:
#         if data['choice'] == 'number':
#             write_doctors_wishes(doctor=doctor, ban_day=[], choice='numbers', file_name='wish_days')
#             await message.answer(f'Для {doctor} список нежелательных для дежурств дат очищен')
#         else:
#             write_doctors_wishes(doctor=doctor, ban_day=[], choice='numbers', file_name='wish_days')
#             await message.answer(f'Для {doctor} список нежелательных для дежурств дней недели очищен')
#
#
# @router.message(F.text == 'Ставить смены')
# async def get_doctor_surname(message: Message, state: FSMContext):
#     await state.set_state(StepWishes.first)
#     doctors = open_data_file('doctors_list.json')
#     builder = InlineKeyboardBuilder()
#     for doctor in doctors.keys():
#         builder.add(InlineKeyboardButton(text=f'{doctors[doctor]}', callback_data=f'{doctors[doctor]}'))
#     builder.adjust(1)
#     await message.answer('Для кого из врачей указать ЖЕЛАТЕЛЬНЫЕ дни дежурств', reply_markup=builder.as_markup())
#
#
# @router.callback_query(StepWishes.first)
# async def select_day_by_number_or_day_week(callback: CallbackQuery, state: FSMContext):
#     await state.update_data(doctor=callback.data)
#     await state.set_state(StepWishes.second)
#     await callback.message.answer(
#         'Вы собираетесь указать конкретные числа или дни недели в которые НУЖНО ставить смены?',
#         reply_markup=select_day_week_or_day_number
#     )
#
#
# @router.callback_query(StepWishes.second)
# async def indicate_days(callback: CallbackQuery, state: FSMContext):
#     await state.update_data(choice=callback.data)
#     if callback.data == 'day_week':
#         await callback.message.answer('Укажите через запятую в какие дни недели НЕ ставить дежурства. '
#                                       'Если требуется очистить список дней, отправьте точку "."')
#     else:
#         await callback.message.answer('Укажите через запятую в какие числа месяца НЕ ставить дежурства. '
#                                       'Если требуется очистить список дней, отправьте точку "."')
#     await state.set_state(StepWishes.third)
#
#
# @router.message(StepWishes.third)
# async def making_changes_to_schedule(message: Message, state: FSMContext):
#     data = await state.get_data()
#     doctor = data['doctor']
#     if message.text != '.':
#         days = message.text.split(', ')
#         if data['choice'] == 'number':
#             write_doctors_wishes(doctor=doctor, ban_day=days, choice='numbers', file_name='wish_days')
#             await message.answer(f'Для {doctor} указаны даты {message.text}', reply_markup=back_button)
#         else:
#             write_doctors_wishes(doctor=doctor, ban_day=days, choice='numbers', file_name='wish_days')
#             await message.answer(f'Для {doctor} указаны дни недели {message.text}', reply_markup=back_button)
#     else:
#         if data['choice'] == 'number':
#             write_doctors_wishes(doctor=doctor, ban_day=[], choice='numbers', file_name='wish_days')
#             await message.answer(f'Для {doctor} список желательных для дежурств дат очищен', reply_markup=back_button)
#         else:
#             write_doctors_wishes(doctor=doctor, ban_day=[], choice='numbers', file_name='wish_days')
#             await message.answer(f'Для {doctor} список желательных для дежурств дней недели очищен', reply_markup=back_button)
            