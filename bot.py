import asyncio
import logging
import aioschedule

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message

from utils import daily_summary


bot = Bot(token='6716211777:AAGJrwvEVLodkQco1VEQNzXx6MheUDXPy1k', parse_mode='HTML')
router = Router()


@router.message(Command(commands=['start']))
async def command_start_handler(message: Message):
    await message.answer('Привет, я - бот для детского травмпункта.')


@router.message()
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
    await bot.send_message(chat_id='-1001396112169', text=text, disable_notification=True)


async def scheduler():
    aioschedule.every().day.at('17:00').do(send_daily_report)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def main():
    dp = Dispatcher()
    dp.include_routers(
        router,
    )
    asyncio.create_task(scheduler())
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())
