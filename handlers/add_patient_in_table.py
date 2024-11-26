from aiogram.utils.keyboard import InlineKeyboardBuilder, InlineKeyboardButton
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery

from utils import connect_to_google_sheets, get_date_and_count_empty_slots, get_date_empty_slots, \
    write_patient_info_in_table

router = Router()


class WriteInTable(StatesGroup):
    step_1 = State()
    step_2 = State()
    step_3 = State()
    step_4 = State()
    step_5 = State()


@router.message(F.text == 'Записать пациента')
async def write_patient(message: Message, state: FSMContext):
    sh = connect_to_google_sheets()
    current_worksheet = sh.get_worksheet_by_id(20174943)
    builder = InlineKeyboardBuilder()
    data = get_date_and_count_empty_slots(current_worksheet.get_all_values())
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
    await state.update_data(diagnosis=message.text)
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
    sh = connect_to_google_sheets()
    current_worksheet = sh.get_worksheet_by_id(20174943)
    builder = InlineKeyboardBuilder()
    data = get_date_and_count_empty_slots(current_worksheet.get_all_values())
    for i in data:
        if data.get(i) > 0:
            builder.row(InlineKeyboardButton(text=i, callback_data=i))
    await callback.message.answer(text='Выберите дату записи', reply_markup=builder.as_markup())
    await state.set_state(WriteInTable.step_1)


@router.callback_query(WriteInTable.step_5, F.data == 'Yes')
async def write_surname(callback: CallbackQuery, state: FSMContext):
    raw_date = await state.get_data()
    date = raw_date.get('date')
    fio = raw_date.get('fio')
    birthday = raw_date.get('birthday')
    diagnosis = raw_date.get('diagnosis')

    sh = connect_to_google_sheets()
    current_worksheet = sh.get_worksheet_by_id(20174943)
    dates_with_empty_address_first_empty_slots = get_date_empty_slots(current_worksheet)
    address_first_empty_cells = dates_with_empty_address_first_empty_slots.get(date)
    address_empty_cell = address_first_empty_cells[0]

    write_patient_info_in_table(
        worksheet=current_worksheet,
        first_cell=address_empty_cell,
        fio_data=fio,
        birthday_data=birthday,
        diagnosis_data=diagnosis
    )

    await callback.message.answer('Запись в таблицу добавлена')
    await state.clear()