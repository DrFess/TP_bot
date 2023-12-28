import asyncio
import logging
import aioschedule

from aiogram import Bot, Dispatcher, Router, F
from aiogram.filters import Command
from aiogram.types import Message

from settings import TOKEN, moders, group_id
from keyboards import wishes_or_ban, moderator_menu
from utils import daily_summary
from handlers import duty_handler, add_month_duty, wish_list, show_doctors_wishes, show_ID

bot = Bot(token=TOKEN, parse_mode='HTML')
router = Router()


@router.message(Command(commands=['start']))
async def command_start_handler(message: Message):
    await message.answer('Привет, я - бот для детского травмпункта.')


@router.message(F.text == '\U0001F519 Назад')
async def back_step(message: Message):
    if message.from_user.id in moders:
        await message.answer('Вам доступно расширенное редактирование графика', reply_markup=moderator_menu)
    else:
        await message.answer(
            f'Вы хотите указать в какие дни ставить или не ставить дежурства? {message.from_user.id}',
            reply_markup=wishes_or_ban
        )


@router.message(F.text == 'Отчет')
async def send_daily_report():
    data = daily_summary()
    if data['экстренных госпитализаций'] == '0':
        text = f'Всего обратилось: {data["всего обратилось"]}\n' \
               f'Экстренных госпитализаций: {data["экстренных госпитализаций"]}'
    else:
        hospitalization = ''
        for item in data['госпитализации']:
            hospitalization += f'\n------\nНомер истории: {item[0]}\nДиагноз: {item[1]}\nПримечание: {item[2]}'
        text = f'Всего обратилось: {data["всего обратилось"]}\n' \
               f'Экстренных госпитализаций: {data["экстренных госпитализаций"]}\n' \
               f'Сведения о госпитализациях: {hospitalization}'
    await bot.send_message(chat_id=group_id, text=text, disable_notification=True)


async def scheduler():
    aioschedule.every().day.at('17:00').do(send_daily_report)
    aioschedule.every().day.at('00:00').do(send_daily_report)
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
        show_ID.router
    )
    asyncio.create_task(scheduler())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
