from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message

from utils import get_dates_you_need, add_days_duty_schedule, formatting_duty_schedule, open_data_file, \
    set_restricted_cells

router = Router()


@router.message(F.text == 'Заполнить график')
async def propose_date(message: Message):
    current_year = datetime.now().year
    current_month = datetime.now().month
    if current_month == 12:
        month = get_dates_you_need(current_year + 1, 1)
        add_days_duty_schedule(month)
        formatting_duty_schedule()
        dates = open_data_file('ban_days.json')
        for doc in dates:
            for item in dates[doc]:
                set_restricted_cells(doc, item, 'X')
        await message.answer(f'Шаблон создан\n'
                             f'Месяц: 1й\n'
                             f'Год: {current_year + 1}')
    else:
        month = get_dates_you_need(current_year, current_month + 1)
        add_days_duty_schedule(month)
        formatting_duty_schedule()
        dates = open_data_file('ban_days.json')
        for doc in dates:
            for item in dates[doc]:
                set_restricted_cells(doc, item, 'X')
        await message.answer(f'Шаблон создан\n'
                             f'Месяц: {current_month + 1}й\n'
                             f'Год: {current_year}')
