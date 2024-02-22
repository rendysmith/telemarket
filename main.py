from openai import AsyncOpenAI
import datetime
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import (
    Message
)
from aiogram.fsm.context import FSMContext
from aiogram.methods import DeleteWebhook

from constants import API_TOKEN, OPEN_TOKEN

bot = Bot(API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher()

client = AsyncOpenAI(api_key=OPEN_TOKEN)

async def get_gpt(prompt: str):
    chat_completion = await client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
        model="gpt-3.5-turbo",
    )

    return chat_completion


@dp.message(Command("start"))
async def command_start_handler(message: Message, state: FSMContext):
    user_name = message.from_user.first_name
    now = datetime.datetime.now()
    hour = now.hour
    if 4 <= hour <= 11:
        tm = 'Доброе утро'

    elif 12 <= hour <= 15:
        tm = 'Доброе день'

    elif 16 <= hour <= 23:
        tm = 'Добрый вечер'

    else:
        tm = 'Доброе время суток'

    await message.answer(f'{tm} {user_name}, меня зовут робот Алёша\n'
                         f'Я буду Вашим помощником в поиске доски для сноуборда\n'
                         f'Для начала мне нужна небольшая информация о тебе:')

    await asyncio.sleep(3)
    await message.answer('1 - Уровень опыта, сколько лет ты уже катаешся? Укажи в годах или поставь 0, если опыта у тебя пока нет.')

@dp.message()
async def handle_message(message: types.Message, state: FSMContext):
    user_name = message.from_user.first_name
    text = message.text

    state_data = await state.get_data()
    print(state_data)

    if state_data.get('experience') == None:
        experience = text
        await state.update_data(experience=experience)
        await message.answer('2 - Укажи свой вес?')

    elif state_data.get('weight') == None:
        weight = text
        await state.update_data(weight=weight)
        await message.answer('3 - Укажи свой рост?')

    elif state_data.get('height') == None:
        height = text
        await state.update_data(height=height)
        await message.answer(f'4 - Отлично {user_name}, теперь скажи какой у тебя стиль катания? Возможно фрирайд или фристайл?:')

    elif state_data.get('style') == None:
        style = text
        await state.update_data(style=style)
        await message.answer(f'5 - Ты будешь кататься для души или хочешь выполнять трюки?:')

    elif state_data.get('_type') == None:
        _type = text
        await state.update_data(_type=_type)
        await message.answer(f'6 - И последнее, будут ли личные предпочтения бренд, дизайн, технологии и т.п.?:')

    elif state_data.get('pers') == None or "еще" in text:
        experience = state_data["experience"]
        weight = state_data["weight"]
        height = state_data["height"]
        style = state_data["height"]
        _type = state_data["_type"]
        pers = text
        await state.update_data(pers=pers)
        await message.answer(f'Ну что же начинаем подбор...')
        await asyncio.sleep(3)
        await message.answer(f'Это займет какое то время...)')

        prompt = ('Как специались по продаже зимнего спортивного инвентаря, подбери доску для сноуборда по следующим параметрам:'
                  f'Уровень опыта: {experience}'
                  f'Вес: {weight}'
                  f'Рост: {height}'
                  f'Стиль катания: {style}'
                  f'Тип террейна: {_type}'
                  f'Личные предпочтения: {pers}')

        data = await get_gpt(prompt)
        await message.answer(f'Вот что я могу вам предложить:')
        await message.answer(data)
        await message.answer(f'Если хотите повторить подбор введите - "еще"\nЕсли хотите изменить настройки подбора введите - "заново"')

    elif 'заново' in text:
        print("++++++++++++")
        await state.clear()
        await message.answer(
            '1 - Уровень опыта, сколько лет ты уже катаешся? Укажи в годах или поставь 0, если опыта у тебя пока нет.')

    state_data = await state.get_data()
    print('+++', state_data)

async def main_bot() -> None:
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)


if __name__ == "__main__":
    print("Start bot!")
    asyncio.run(main_bot())