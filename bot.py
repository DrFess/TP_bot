import os

import asyncio
import logging
import aioschedule

from aiogram import Bot, Dispatcher, Router
from aiogram.filters import Command
from aiogram.types import Message

from utils import daily_summary


print(os.getenv('TOKEN'))
bot = Bot(token=os.getenv('TOKEN'), parse_mode='HTML')
router = Router()


@router.message(Command(commands=['start']))
async def command_start_handler(message: Message):
    await message.answer('Привет, я - бот для детского травмпункта.')


@router.message()
async def send_daily_report():
    data = daily_summary()
    if data['экстренных госпитализаций'] == 0:
        text = f'Всего обратилось: {data["всего обратилось"]}\n' \
               f'Экстренных госпитализация: {data["экстренных госпитализаций"]}'
    else:
        hospitalization = ''
        for item in data['госпитализации']:
            hospitalization.join(f'Номер истории: {item[0]}\n'
                                 f'Диагноз: {item[1]}\n'
                                 f'Примечание: {item[2]}\n')

        text = f'Всего обратилось: {data["всего обратилось"]}\n' \
               f'Экстренных госпитализация: {data["экстренных госпитализаций"]}\n' \
               f'Сведения о госпитализациях: {hospitalization}'
    await bot.send_message(chat_id=os.getenv('GROUP_ID'), text=text)


async def scheduler():
    aioschedule.every().day.at('17:45').do(send_daily_report)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)

# async def on_startup(dp):
#     asyncio.create_task(scheduler())


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
