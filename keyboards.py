from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


back_button = [KeyboardButton(text=f'\U0001F519 Назад')]

wishes_or_ban = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text='Ставить смены')], [KeyboardButton(text='Не ставить смены')]],
    one_time_keyboard=True,
    resize_keyboard=True
)

moderator_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='Ставить смены')],
        [KeyboardButton(text='Не ставить смены')],
        [KeyboardButton(text='Очистить график')],
        [KeyboardButton(text='Заполнить график')],
    ],
    one_time_keyboard=True,
    resize_keyboard=True
)