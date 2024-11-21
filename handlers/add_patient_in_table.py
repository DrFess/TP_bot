from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton,\
    ReplyKeyboardBuilder
from aiogram import types, F, Router
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, KeyboardButton, CallbackQuery


router = Router()


class WriteInTable(StatesGroup):
    step_1 = State()
    step_2 = State()
    step_3 = State()
    step_4 = State()
    step_5 = State()


def some_func():
    pass


@router.message(Command('start'))
async def cmd_start(message: types.Message):
    builder = ReplyKeyboardBuilder()
    builder.add(KeyboardButton(text="Записать пациента"))
    await message.answer(text='test', reply_markup=builder.as_markup())


@router.message(F.text=='Записать пациента')
async def write_patient(message: Message, state: FSMContext):
    builder = InlineKeyboardBuilder()
    data = {'02.12.2024': 5, '05.12.2024': 3, '09.12.2024': 0, '12.12.2024': 3}
    for i in data:
        if data.get(i) > 0:
            builder.row(InlineKeyboardButton(text=i, callback_data=i))
    await message.answer(text='Выберите дату записи', reply_markup=builder.as_markup())
    await state.set_state(WriteInTable.step_1)


@router.callback_query(WriteInTable.step_1)
async def take_date_and_answer_fio(callback: CallbackQuery, state: FSMContext):
    data = callback.data
    await state.update_data(date=data)
    await callback.message.answer('Введи ФИО')
    await state.set_state(WriteInTable.step_2)


@router.message(WriteInTable.step_2)
async def take_fio_answer_birthday(message: Message, state: FSMContext):
    await state.update_data(fio=message.text)
    await message.answer('Введите дату рождения')
    await state.set_state(WriteInTable.step_3)


@router.message(WriteInTable.step_3)
async def take_birthday_answer_diagnosis(message: Message, state: FSMContext):
    await state.update_data(birthday=message.text)
    await message.answer('Введите диагноз')
    await state.set_state(WriteInTable.step_4)


@router.message(WriteInTable.step_4)
async def take_diagnosis_answer_all_data(message: Message, state: FSMContext):
    all_data = await state.get_data()
    patient = all_data.get('fio')
    date = all_data.get('date')
    builder = InlineKeyboardBuilder()
    builder.row(InlineKeyboardButton(text='Да', callback_data='Yes'))
    builder.row(InlineKeyboardButton(text='Нет', callback_data='No'))
    await message.answer(f'Записать {patient} на {date}?', reply_markup=builder.as_markup())
    await state.set_state(WriteInTable.step_5)


@router.callback_query(WriteInTable.step_5, F.data == 'No')
async def write_patient(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    builder = InlineKeyboardBuilder()
    data = {'02.12.2024': 5, '05.12.2024': 3, '09.12.2024': 0, '12.12.2024': 3}  # данные для примера и тестирования
    for i in data:
        if data.get(i) > 0:
            builder.row(InlineKeyboardButton(text=i, callback_data=i))
    await callback.message.answer(text='Выберите дату записи', reply_markup=builder.as_markup())
    await state.set_state(WriteInTable.step_1)


@router.callback_query(WriteInTable.step_5, F.data == 'Yes')
async def write_surname(callback: CallbackQuery, state: FSMContext):
    data = callback.message.text
    raw_date = await state.get_data()
    date = raw_date.get('date')
    some_func()
    await callback.message.answer('Запись в таблицу добавлена.')
    await state.clear()
