import asyncio
import logging
import datetime

import aioschedule

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message

from database.db import create_tables, add_weekday, get_doctor_telegram_id_by_surname
from settings import TOKEN, moders, group_id, WEEK_DAYS, department_doctors
from keyboards import wishes_or_ban_TP, moderator_menu, wishes_or_ban_department
from utils import daily_summary, get_patients_info, create_text_report
from handlers import duty_handler, add_month_duty, wish_list, show_doctors_wishes, show_ID, add_doctor, \
    show_patients_for_doctor

bot = Bot(token=TOKEN, parse_mode='HTML')
router = Router()


@router.message(Command(commands=['start']))
async def command_start_handler(message: Message):
    await message.answer('Привет, я - бот для детского травмпункта.')


@router.message(Command(commands=['create_db']))
async def create_db(message: Message):
    create_tables()
    await message.answer('Таблицы созданы')


@router.message(Command(commands=['weekday']))
async def add_weekdays(message: Message):
    for day in WEEK_DAYS:
        add_weekday(day, WEEK_DAYS.get(day))
    await message.answer('Дни недели добавлены')


@router.message(F.text.in_({'\U0001F519 Назад', 'Меню'}))
async def back_step(message: Message):
    if message.from_user.id in moders:
        await message.answer('Вам доступно расширенное редактирование графика', reply_markup=moderator_menu)
    elif message.from_user.id in department_doctors:
        await message.answer('Основное меню', reply_markup=wishes_or_ban_department)
    else:
        await message.answer(
            f'Вы хотите указать в какие дни ставить или не ставить дежурства? {message.from_user.id}',
            reply_markup=wishes_or_ban_TP
        )


@router.message(F.text == 'Отчет')
async def send_daily_report():
    data = daily_summary()
    if data['экстренных госпитализаций'] == '0':
        text = f'За {datetime.date.today().strftime("%d.%m.%Y")} всего обратилось: {data["всего обратилось"]}\n' \
               f'Экстренных госпитализаций: {data["экстренных госпитализаций"]}\n' \
               f'\U0001F3E5\n' \
               f'Пациентов в травматологии всего/присутствует: {data["пациентов в травматологии всего/присутствует"]}'
    else:
        hospitalization = ''
        for item in data['госпитализации']:
            hospitalization += f'\n\U0001F6CF\nНомер истории: {item[0]}\nДиагноз: {item[1]}\nПримечание: {item[2]}'
        text = f'За {datetime.date.today().strftime("%d.%m.%Y")} всего обратилось: {data["всего обратилось"]}\n' \
               f'Экстренных госпитализаций: {data["экстренных госпитализаций"]}\n' \
               f'Сведения о госпитализациях: {hospitalization}\n' \
               f'\U0001F3E5\n' \
               f'Пациентов в травматологии всего/присутствует: {data["пациентов в травматологии всего/присутствует"]}'
    await bot.send_message(chat_id=group_id, text=text, disable_notification=True)


@router.message(F.text == 'Отчет')
async def send_daily_report_morning():
    data = daily_summary()
    if data['экстренных госпитализаций'] == '0':
        text = f'За 8 часов {datetime.date.today().strftime("%d.%m.%Y")} всего обратилось: {data["всего обратилось"]}\n' \
               f'Экстренных госпитализаций: {data["экстренных госпитализаций"]}\n' \
               f'\U0001F3E5\n' \
               f'Пациентов в травматологии всего/присутствует: {data["пациентов в травматологии всего/присутствует"]}'
    else:
        hospitalization = ''
        for item in data['госпитализации']:
            hospitalization += f'\n\U0001F6CF\nНомер истории: {item[0]}\nДиагноз: {item[1]}\nПримечание: {item[2]}'
        text = f'За 8 часов {datetime.date.today().strftime("%d.%m.%Y")} всего обратилось: {data["всего обратилось"]}\n' \
               f'Экстренных госпитализаций: {data["экстренных госпитализаций"]}\n' \
               f'Сведения о госпитализациях: {hospitalization}\n' \
               f'\U0001F3E5\n' \
               f'Пациентов в травматологии всего/присутствует: {data["пациентов в травматологии всего/присутствует"]}'
    await bot.send_message(chat_id=group_id, text=text, disable_notification=True)


# async def show_patients_schedule():
#     all_patients = get_patients_info()
#     for doctor in all_patients.keys():
#         telegram_id = get_doctor_telegram_id_by_surname(doctor)
#         text = create_text_report(telegram_id)
#         await bot.send_message(chat_id=telegram_id, text=text, disable_notification=True)


async def scheduler():
    aioschedule.every().day.at('17:00').do(send_daily_report)
    aioschedule.every().day.at('00:01').do(send_daily_report_morning)
    # aioschedule.every().day.at('04:30').do(show_patients_schedule)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def main():
    dp = Dispatcher()
    dp.include_routers(
        router,
        duty_handler.router,
        add_month_duty.router,
        wish_list.router,
        show_doctors_wishes.router,
        show_ID.router,
        add_doctor.router,
        show_patients_for_doctor.router,
    )
    asyncio.create_task(scheduler())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
