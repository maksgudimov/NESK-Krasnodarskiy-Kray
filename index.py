from aiogram import Bot, Dispatcher, executor, types
from aiogram.dispatcher.filters import Text
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup
from emoji import emojize
import advertools as adv #для отслеживания эмодзи

import logging
import requests
import sqlite3 as sq
import sqlite3
import datetime



storage = MemoryStorage() #создание объекта класса оперативной памяти

bot = Bot(token="TOKEN") #подключение токена

dp = Dispatcher(bot,storage=storage) #создание диспетчера с доступом хранения в оперативную память

logging.basicConfig(level=logging.INFO)
# Включаем логирование, чтобы не пропустить важные сообщения

async def on_startup(_):
    print('Бот вышел в онлайн')
    global base, cur
    base = sq.connect('main.db')
    cur = base.cursor()
    if base:
        print('Data base connected OK!')
    base.execute('CREATE TABLE IF NOT EXISTS users(id INTEGER,datatime REAL,call INTEGER,link TEXT, phone INTEGER, question TEXT,PRIMARY KEY("id" AUTOINCREMENT))')
    base.commit()

async def sql_add(state):
    async with state.proxy() as data:
        cur.execute('INSERT INTO users(datatime,call,link,phone,question) VALUES (?,?,?,?,?)',
                    tuple(data.values()))
        base.commit()

def kb_start():
    kb_starting = types.InlineKeyboardMarkup(row_width=1)
    starting_b1 = types.InlineKeyboardButton(text=f"Начать {emojize(':check_mark_button:')}", callback_data="starting")
    kb_starting.add(starting_b1)
    return kb_starting

def kb_question():
    kb_quest = types.InlineKeyboardMarkup(row_width=1)
    quest_b1 = types.InlineKeyboardButton(text=f"Оставить заявку", callback_data="quest_yes")
    quest_b2 = types.InlineKeyboardButton(text=f"Вернуться в начало", callback_data="quest_no")
    kb_quest.add(quest_b1,quest_b2)
    return kb_quest

def kb_in():
    kb_inner = types.InlineKeyboardMarkup(row_width=2)
    inner_b1 = types.InlineKeyboardButton(text=f"Да", callback_data="inner_yes")
    inner_b2 = types.InlineKeyboardButton(text=f"Нет", callback_data="inner_no")
    kb_inner.add(inner_b1,inner_b2)
    return kb_inner

class Question(StatesGroup):
    q_from_user = State()
    phone = State()

class Search(StatesGroup):
    city = State()
    street = State()

async def start(message:types.Message,state: FSMContext):
    print(message.chat.id)
    await state.finish()
    await bot.send_message(message.chat.id,f"Вас приветствует бот-помощник НЭСК! Здесь вы можете проверить "
                                           f"отключение по вашему адресу.\n\nВведите населенный пункт, где произошло отключение\n\nПример: Краснодар")
    await Search.city.set()

async def contacts(message:types.Message,state: FSMContext):
    print(message.chat.id)
    await state.finish()
    await bot.send_message(message.chat.id,f"Единый номер для приёма обращений потребителей:\n\n+7(861) 944-77-40\n+7(903) 411-77-40\n8-800-600-02-20\nЭлектронная почта: contact@nesk.ru\n\nЧтобы вернуться в начало - нажмите /start")



async def welcome_button(callback:types.CallbackQuery,state: FSMContext):
    await bot.answer_callback_query(callback.id)
    await bot.delete_message(callback.from_user.id, callback.message.message_id)
    await bot.send_message(callback.from_user.id,f"Введите населенный пункт, где произошло отключение\n\nПример: Краснодар")
    await Search.city.set()

async def city(message:types.Message,state: FSMContext):
    if message.text == "/start":
        await start(message,state)
        return
    if message.text == "/contacts":
        await contacts(message,state)
        return
    print(message.content_type)
    print(adv.extract_emoji(message.text)['overview']['num_emoji'])
    if message.content_type != 'text' or adv.extract_emoji(message.text)['overview']['num_emoji'] >=1:
        await bot.send_message(message.chat.id,
                               f"Бот принимает только текстовое сообщение.\n\nПожалуйста, убедитесь, что ваше сообщение не содержит эмодзи,фото, видео или аудио.\n\nОтправьте ваш населенный пункт заново")
        await Search.city.set()
    else:
        async with state.proxy() as data:
            data['city'] = message.text
            await bot.send_message(message.chat.id, f"Ваш город - {data['city']}\n\nВведите улицу\n\nПример: Красная")
        await Search.street.set()


async def street(message:types.Message,state: FSMContext):
    if message.text == "/start":
        await start(message,state)
        return
    if message.text == "/contacts":
        await contacts(message,state)
        return
    if message.content_type != 'text' or adv.extract_emoji(message.text)['overview']['num_emoji'] >=1:
        await bot.send_message(message.chat.id,
                               f"Бот принимает только текстовое сообщение.\n\nПожалуйста, убедитесь, что ваше сообщение не содержит эмодзи,фото, видео или аудио.\n\nОтправьте вашу улицу заново")
        await Search.street.set()
    else:
        async with state.proxy() as data:
            data['street'] = message.text
            try:
                URL = f"http://10.101.17.150/api/service/newsearch/?city={data['city']}&street={data['street']}"
                page = requests.get(f"{URL}")
                js = page.json()
                if js['MESSAGE'] == "Аварийные и плановые отключения в вашем районе отсутствуют. Для подачи заявки оставайтесь на линии, Вам ответит первый освободившийся оператор.":
                    await bot.send_message(message.chat.id,
                                           f"Ваш город - {data['city']}\n\nВаша улица - {data['street']}\n\nАварийные и плановые отключения в вашем районе отсутствуют.\n\nХотите оставить заявку?",
                                           reply_markup=kb_question())

                if "Скажите да или нет." in js['MESSAGE']:
                    str = js['MESSAGE'].split(";")[0]
                    await bot.send_message(message.chat.id,
                                           f"Ваш город - {data['city']}\n\nВаша улица - {data['street']}\n\n{str}\n\nОзвучены все отключения в Вашем населенном пункте. Подскажите, пожалуйста, Ваша улица вошла в район отключений?\n\n(Нажмите)",
                                           reply_markup=kb_in())

                if "По Вашему адресу" in js['MESSAGE']:
                    await bot.send_message(message.chat.id,
                                           f"Ваш город - {data['city']}\n\nВаша улица - {data['street']}\n\n{js['MESSAGE']}\n\n Для того, чтобы начать сначала - нажмите на кнопку",
                                           reply_markup=kb_start())

                if "Вы не идентифицированы как клиент НЭСК." in js['MESSAGE']:
                    await bot.send_message(message.chat.id,
                                           f"Ваш город - {data['city']}\n\nВаша улица - {data['street']}\n\n{js['MESSAGE']}\n\nДля того, чтобы начать сначала - нажмите на кнопку",
                                           reply_markup=kb_start())



            except:
                await bot.send_message(message.chat.id,
                                       f"На данный момент сервис недоступен, попробуйте попытку позже\n\nДля начала работы нажмите - /start")
        await state.finish()


async def quest(callback:types.CallbackQuery,state: FSMContext):
    await bot.answer_callback_query(callback.id)
    str = callback.data.split("_")[1]
    if str == "yes":
        await bot.send_message(callback.from_user.id,f"Напишите ваш номер телефона: ")
        await Question.phone.set()
    if str == "no":
        await state.finish()
        await bot.send_message(callback.from_user.id, f"Вас приветствует бот-помощник НЭСК! Здесь вы можете проверить "
                                                f"отключение по вашему адресу.\n\nВведите населенный пункт, где произошло отключение\n\nПример: Краснодар")
        await Search.city.set()
        #await start(message,state)
        #await bot.send_message(callback.from_user.id,f"Чтобы начать сначала - нажмите на кнопку",reply_markup=kb_start())

async def phone(message:types.Message,state: FSMContext):
    if message.text == "/start":
        await start(message,state)
        return
    if message.text == "/contacts":
        await contacts(message,state)
        return
    print(message.content_type)
    if message.content_type != 'text' or adv.extract_emoji(message.text)['overview']['num_emoji'] >=1:
        await bot.send_message(message.chat.id,
                               f"Бот принимает только текстовое сообщение.\n\nПожалуйста, убедитесь, что ваше сообщение не содержит эмодзи,фото, видео или аудио.\n\nОтправьте ваш номер телефона заново")
        await Question.phone.set()
    else:
        await Question.phone.set()
        async with state.proxy() as data:
            data['datatime'] = datetime.date.today()
            data['call'] = message.chat.id
            data['link'] = message.from_user.username
            data['phone'] = message.text
        await bot.send_message(message.chat.id, f"Отлично! Опишите Ваш вопрос или проблему:")
        await Question.q_from_user.set()





async def question(message:types.Message,state: FSMContext):
    if message.text == "/start":
        await start(message,state)
        return
    if message.text == "/contacts":
        await contacts(message,state)
        return
    print(message.content_type)
    if message.content_type != 'text' or adv.extract_emoji(message.text)['overview']['num_emoji'] >=1:
        await bot.send_message(message.chat.id,
                               f"Бот принимает только текстовое сообщение.\n\nПожалуйста, убедитесь, что ваше сообщение не содержит эмодзи,фото, видео или аудио.\n\nОтправьте ваш вопрос заново")
        await Question.q_from_user.set()
    else:
        async with state.proxy() as data:
            data['q_from_user'] = message.text
        await sql_add(state)
        await bot.send_message(message.chat.id, f"Спасибо, скоро с вами свяжутся! "
                                                f"Чтобы начать заново - нажмите на кнопку", reply_markup=kb_start())
        await state.finish()



async def inner(callback:types.CallbackQuery,state: FSMContext):
    await bot.answer_callback_query(callback.id)
    str = callback.data.split("_")[1]
    if str == "yes":
        await bot.send_message(callback.from_user.id,f"Чтобы начать сначала - нажмите на кнопку",reply_markup=kb_start())
    if str == "no":
        await bot.send_message(callback.from_user.id,f"Хотите оставить заявку?",reply_markup=kb_question())


if __name__ == "__main__":
    dp.register_message_handler(start, commands=['start'], state=None)
    dp.register_message_handler(contacts, commands=['contacts'], state=None)
    dp.register_message_handler(city, content_types=['any'], state=Search.city)
    dp.register_message_handler(street, content_types=['any'], state=Search.street)
    dp.register_message_handler(phone, content_types=['any'],state=Question.phone)
    dp.register_message_handler(question, content_types=['any'], state=Question.q_from_user)

    dp.register_callback_query_handler(welcome_button, Text(startswith='starting'), state=None)
    dp.register_callback_query_handler(quest, Text(startswith='quest_'), state=None)
    dp.register_callback_query_handler(inner, Text(startswith='inner_'), state=None)

    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
