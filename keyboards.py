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
        [KeyboardButton(text='Показать пожелания врачей')],
    ],
    one_time_keyboard=True,
    resize_keyboard=True
)

select_day_week_or_day_number = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='Дни недели', callback_data='day_week')],
        [InlineKeyboardButton(text='Числа', callback_data='number')]
    ]
)