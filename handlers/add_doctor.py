from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, InlineKeyboardButton, CallbackQuery
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database.db import add_doctor, show_all_doctors, edit_doctor_info
from keyboards import yes_or_no, back_button

router = Router()


class AddingDoctor(StatesGroup):
    surname = State()
    name = State()
    patronymic = State()
    yes_or_no_step = State()


class EditProfiles(StatesGroup):
    first = State()
    second = State()


@router.message(F.text == 'Добавить врача в базу данных')
async def add_doctor_start(message: Message, state: FSMContext):
    await message.answer('Укажи фамилию врача')
    await state.set_state(AddingDoctor.surname)


@router.message(AddingDoctor.surname)
async def add_doctor_surname(message: Message, state: FSMContext):
    await state.update_data(surname=message.text)
    await message.answer('Укажи имя врача')
    await state.set_state(AddingDoctor.name)


@router.message(AddingDoctor.name)
async def add_doctor_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await message.answer('Укажи отчество врача')
    await state.set_state(AddingDoctor.patronymic)


@router.message(AddingDoctor.patronymic)
async def add_doctor_patronymic(message: Message, state: FSMContext):
    await state.update_data(patronymic=message.text)
    data = await state.get_data()
    await message.answer(f'Проверим?\n'
                         f'Фамилия: {data["surname"]}\n'
                         f'Имя: {data["name"]}\n'
                         f'Отчество: {data["patronymic"]}\n'
                         f'Верно?', reply_markup=yes_or_no)
    await state.set_state(AddingDoctor.yes_or_no_step)


@router.message(AddingDoctor.yes_or_no_step)
async def add_doctor_yes_or_no(message: Message, state: FSMContext):
    if message.text == 'Да':
        data = await state.get_data()
        add_doctor(None, data['surname'], data['name'], data['patronymic'])
        await message.answer('Врач добавлен')
        await state.clear()
    else:
        await message.answer('Отмена', reply_markup=back_button)
        await state.clear()


@router.message(F.text == 'Добавить telegram_id врача в базу данных')
async def show_all_doctors_message(message: Message, state: FSMContext):
    data = show_all_doctors()
    builder = InlineKeyboardBuilder()
    for doc in data:
        builder.row(InlineKeyboardButton(text=f"{data.get(doc)['фамилия']} {data.get(doc)['имя']}", callback_data=f'{doc}'))
    await message.answer('Выберите врача для изменения его telegram_id', reply_markup=builder.as_markup())
    await state.set_state(EditProfiles.first)


@router.callback_query(EditProfiles.first, F.data.in_({str(x) for x in range(1, 20)}))
async def edit_doctor_profile(callback: CallbackQuery, state: FSMContext):
    await state.update_data(doc_id=callback.data)
    await callback.message.answer('Введите telegram_id')
    await state.set_state(EditProfiles.second)


@router.message(EditProfiles.second)
async def edit_doctor_profile_message(message: Message, state: FSMContext):
    data = await state.get_data()
    edit_doctor_info(int(message.text), data['doc_id'])
    await message.answer('telegram_id добавлен')
    await state.clear()
