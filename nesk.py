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
# import sqlite3 as sq
# import sqlite3
import datetime

from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.webhook import SendMessage, DEFAULT_ROUTE_NAME
from aiogram.utils.executor import start_webhook
from aiohttp import web as aiohttp_web
from aiogram.utils.executor import set_webhook

#import pymysql.cursors

import smtplib
import aiosmtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import traceback


API_TOKEN = '5946911948:AAGP8aZjw8o2XHeXdI3hbqQ1a3JIE0WMfYA'

WEBHOOK_HOST = 'https://telega.it-spectrum.tech:8443' #telega.it-spectrum.tech https://telega.it-spectrum.tech:8443
WEBHOOK_PATH = '/webhook' # тут оставь пустым
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

WEBAPP_HOST = '92.63.105.205'  # or ip http://telega.it-spectrum.tech/ 92.63.105.205 0 0 0 0 localhost
WEBAPP_PORT = 6060

logging.basicConfig(level=logging.INFO)

storage = MemoryStorage() #создание объекта класса оперативной памяти

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot,storage=storage)
dp.middleware.setup(LoggingMiddleware())

routes = aiohttp_web.RouteTableDef()

@routes.get('/')
async def hello(request):
    return aiohttp_web.Response(text="Working")

app = aiohttp_web.Application()
app.add_routes(routes)



async def on_startup(_):
    await bot.set_webhook(WEBHOOK_URL)
    print('BOT IS ONLINE')



    # global base,cur
    # base = pymysql.connect(host="localhost",
    #                        user="root",
    #                        password="nesk2023",
    #                        db="main",
    #                        charset='utf8',
    #                        port=3306
    #                        )
    # cur = base.cursor()
    # if base:
    #     print('Data base connected OK!')
    # # cur.execute(
    # #     'CREATE TABLE IF NOT EXISTS users(id INTEGER,datatime REAL,call INTEGER,link TEXT, phone INTEGER, question TEXT,PRIMARY KEY("id" AUTOINCREMENT))')
    # # base.commit()
    # cur.execute(
    #     'CREATE TABLE IF NOT EXISTS users(Id int PRIMARY KEY AUTO_INCREMENT,Datatime text,Callback int,Link text, Phone int, Question text)')
    # base.commit()


#     print('Data base connected OK!')
    # global base, cur
    # base = sq.connect('main.db')
    # cur = base.cursor()
    # if base:
    #     print('Data base connected OK!')
    # base.execute('CREATE TABLE IF NOT EXISTS users(id INTEGER,datatime REAL,call INTEGER,link TEXT, phone INTEGER, question TEXT,PRIMARY KEY("id" AUTOINCREMENT))')
    # base.commit()
#CREATE TABLE IF NOT EXISTS users(id INTEGER,datatime REAL,call INTEGER,link VARCHAR(128), phone INTEGER, question VARCHAR(1024),PRIMARY KEY("id" AUTOINCREMENT))
#CREATE TABLE users(id INTEGER,datatime REAL,call INTEGER,link TEXT, phone INTEGER, question TEXT,PRIMARY KEY("id" AUTOINCREMENT))
# async def sql_add(state):
#     async with state.proxy() as data:
#         cur.execute('INSERT INTO users(Datatime,Callback,link,phone,question) VALUES (%s,%s,%s,%s,%s)',
#                     tuple(data.values()))
#         base.commit()

def kb_start():
    kb_starting = types.InlineKeyboardMarkup(row_width=1)
    starting_b1 = types.InlineKeyboardButton(text=f"Начать {emojize(':check_mark_button:')}", callback_data="starting")
    kb_starting.add(starting_b1)
    return kb_starting

def kb_question():
    kb_quest = types.InlineKeyboardMarkup(row_width=1)
    quest_b1 = types.InlineKeyboardButton(text=f"Оставить информацию, без ответа", callback_data="quest_info")
    quest_b2 = types.InlineKeyboardButton(text=f"Вернуться в начало", callback_data="quest_no")
    kb_quest.add(quest_b1,quest_b2)#(quest_b1,
    return kb_quest

def kb_in():
    kb_inner = types.InlineKeyboardMarkup(row_width=2)
    inner_b1 = types.InlineKeyboardButton(text=f"Да", callback_data="inner_yes")
    inner_b2 = types.InlineKeyboardButton(text=f"Нет", callback_data="inner_no")
    kb_inner.add(inner_b1,inner_b2)
    return kb_inner


class Question(StatesGroup):
    q_from_user = State()
    #phone = State()

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
    #await bot.delete_message(callback.from_user.id, callback.message.message_id)
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
            try:
                URL = f"http://10.101.17.150/api/service/newsearch/?city={data['city']}&street=а"
                page = requests.get(f"{URL}")
                js = page.json()
            except:
                await bot.send_message(message.chat.id,
                                       f"На данный момент сервис недоступен, попробуйте попытку позже\n\nДля начала работы нажмите - /start")
            if "Вы не идентифицированы как клиент НЭСК." in js['MESSAGE']:
                await bot.send_message(message.chat.id,
                                       f"Ваш город - {data['city']}\n\n{js['MESSAGE']}\n\nДля того, чтобы начать сначала - нажмите на кнопку",
                                       reply_markup=kb_start())
                await state.finish()
            else:
                await bot.send_message(message.chat.id,
                                       f"Ваш город - {data['city']}\n\nВведите улицу\n\nПример: Красная")
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
                #print(js['MESSAGE'])
                dict ={
                    'Полночь': '00:00',

                    'Час ночи': '01:00',
                    'Два часа ночи': '02:00',
                    'Три часа ночи': '03:00',
                    'Четыре часа утра ': '04:00',
                    'Пять часов утра': '05:00',
                    'Шесть часов утра': '06:00',
                    'Семь часов утра': '07:00',
                    'Восемь часов утра': '08:00',
                    'Девять часов утра': '09:00',
                    'Десять часов утра': '10:00',
                    'Одиннадцать часов утра': '11:00',
                    'Полдень': '12:00',

                    'Час дня': '13:00',
                    'Два часа дня': '14:00',
                    'Три часа дня': '15:00',
                    'Четыре часа дня': '16:00',
                    'Пять часов вечера': '17:00',
                    'Шесть часов вечера': '18:00',
                    'Семь часов вечера': '19:00',
                    'Восемь часов вечера': '20:00',
                    'Девять часов вечера': '21:00',
                    'Десять часов вечера': '22:00',
                    'Одиннадцать часов вечера': '23:00'
                }
                for i, j in zip(dict.keys(), dict.values()):
                    if i in js['MESSAGE']:
                        js['MESSAGE'] = js['MESSAGE'].replace(i,j)

                if js['MESSAGE'] == "Аварийные и плановые отключения в вашем районе отсутствуют. Для подачи заявки оставайтесь на линии, Вам ответит первый освободившийся оператор.":
                    await bot.send_message(message.chat.id,
                                           f"Ваш город - {data['city']}\n\nВаша улица - {data['street']}\n\nИнформация о плановых и аварийных отключениях в вашем районе отсутствует."
                                           f"Рекомендуем подать заявку об отключении электроэнергии в управляющую компанию МКД или по телефону Горячей линии АО «НЭСК-электросети» +78002348373.\n\nВы можете вернуться в начало, нажав на кнопку, или оставить информацию.",
                                           reply_markup=kb_question())
                    print("IN IF 1")


                if "имеется аварийное отключение." in js['MESSAGE']:
                    str = js['MESSAGE'].split("Озвучены все отключения в Вашем населенном пункте.")[0]
                    await bot.send_message(message.chat.id,
                                           f"Ваш город - {data['city']}\n\nВаша улица - {data['street']}\n\n{str}\n\nОзвучены все отключения в Вашем населенном пункте. Вы можете вернуться в начало, нажав на кнопку, оставить информацию, или позвонить на горячую линию.\n\nНомер телефона горячей линии:\n\n8-800-600-02-20",
                                           reply_markup=kb_question())
                    print("IN IF 2")



                if "запланировано отключение электроэнергии" in js['MESSAGE']: #if "Ориентировочное время" in js['MESSAGE']:
                    await bot.send_message(message.chat.id,
                                           f"Ваш город - {data['city']}\n\nВаша улица - {data['street']}\n\n{js['MESSAGE']}\n\n Для того, чтобы начать сначала - нажмите на кнопку.",
                                           reply_markup=kb_start())
                    print("IN IF 3")

                # if "имеется аварийное отключение." in js['MESSAGE']: #if "Ориентировочное время" in js['MESSAGE']:
                #     await bot.send_message(message.chat.id,
                #                            f"Ваш город - {data['city']}\n\nВаша улица - {data['street']}\n\n{js['MESSAGE']}\n\n Для того, чтобы начать сначала - нажмите на кнопку.",
                #                            reply_markup=kb_start())
                #     print("IN IF 4")

                # if "имеется аварийное отключение" in js['MESSAGE']: #if "Ориентировочное время" in js['MESSAGE']:
                #     await bot.send_message(message.chat.id,
                #                            f"Ваш город - {data['city']}\n\nВаша улица - {data['street']}\n\n{js['MESSAGE']}\n\n Для того, чтобы начать сначала - нажмите на кнопку",
                #                            reply_markup=kb_start())
                #     print("IN IF 4")


                # if "Вы не идентифицированы как клиент НЭСК." in js['MESSAGE']:
                #     await bot.send_message(message.chat.id,
                #                            f"Ваш город - {data['city']}\n\nВаша улица - {data['street']}\n\n{js['MESSAGE']}\n\nДля того, чтобы начать сначала - нажмите на кнопку",
                #                            reply_markup=kb_start())

            except Exception as exc:
                print(f"{exc}, full: {traceback.format_exc()}")
                await bot.send_message(message.chat.id,
                                       f"На данный момент сервис недоступен, попробуйте попытку позже\n\nДля начала работы нажмите - /start")
        await state.finish()


async def quest(callback:types.CallbackQuery,state: FSMContext):

    str = callback.data.split("_")[1]
    if str == "info":
        await bot.answer_callback_query(callback.id)
        await bot.send_message(callback.from_user.id, f"Пожалуйста, внесите текст.")
        await Question.q_from_user.set()

    # if str == "phone":
    #     await bot.answer_callback_query(callback.id,show_alert=True, text="Номер телефона горячей линии:\n\n8-800-600-02-20")
        #await bot.answer_callback_query(callback.id,show_alert=True, text="8-800-600-02-20")
        #await bot.send_message(callback.from_user.id,f"Напишите ваш номер телефона: ")
        #await Question.phone.set()
    if str == "no":
        await bot.answer_callback_query(callback.id)
        await state.finish()
        await bot.send_message(callback.from_user.id, f"Вас приветствует бот-помощник НЭСК! Здесь вы можете проверить "
                                                f"отключение по вашему адресу.\n\nВведите населенный пункт, где произошло отключение\n\nПример: Краснодар")
        await Search.city.set()
        #await start(message,state)
        #await bot.send_message(callback.from_user.id,f"Чтобы начать сначала - нажмите на кнопку",reply_markup=kb_start())

# async def phone(message:types.Message,state: FSMContext):
#     if message.text == "/start":
#         await start(message,state)
#         return
#     if message.text == "/contacts":
#         await contacts(message,state)
#         return
#     print(message.content_type)
#     if message.content_type != 'text' or adv.extract_emoji(message.text)['overview']['num_emoji'] >=1:
#         await bot.send_message(message.chat.id,
#                                f"Бот принимает только текстовое сообщение.\n\nПожалуйста, убедитесь, что ваше сообщение не содержит эмодзи,фото, видео или аудио.\n\nОтправьте ваш номер телефона заново")
#         await Question.phone.set()
#     else:
#         await Question.phone.set()
#         async with state.proxy() as data:
#             data['datatime'] = str(datetime.date.today())
#             data['call'] = message.chat.id
#             data['link'] = message.from_user.username
#             data['phone'] = message.text
#         await bot.send_message(message.chat.id, f"Отлично! Опишите Ваш вопрос или проблему:")
#         await Question.q_from_user.set()





async def question(message:types.Message,state: FSMContext):
    # smtpObj = smtplib.SMTP('smtp.yandex.ru', 587)
    # smtpObj.starttls()
    # smtpObj.login('telega_test@it-spectrum.tech', 'tXz-6v3-zS5-XFF')
    SMTP_CLIENT = aiosmtplib.SMTP(
        hostname="smtp.yandex.ru",
        port=465,
        username="telega_test@it-spectrum.tech",
        password="tXz-6v3-zS5-XFF",
        use_tls=True
    )


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
            msg = MIMEText(data['q_from_user'])
            async with SMTP_CLIENT:
                await SMTP_CLIENT.sendmail("telega_test@it-spectrum.tech", "cto@it-spectrum.tech",msg.as_string())

            #smtpObj.sendmail("telega_test@it-spectrum.tech","telega_test@it-spectrum.tech", msg.as_string()) #maks.gudimov.90@mail.ru
        #await sql_add(state)

        await bot.send_message(message.chat.id, f"Спасибо. Ваша информация принята к сведению.\n\n"
                                                f"Чтобы начать заново - нажмите на кнопку", reply_markup=kb_start())
        #smtpObj.quit()
        await state.finish()


async def inner(callback:types.CallbackQuery,state: FSMContext):
    await bot.answer_callback_query(callback.id)
    str = callback.data.split("_")[1]
    if str == "yes":
        await bot.send_message(callback.from_user.id,f"Чтобы начать сначала - нажмите на кнопку",reply_markup=kb_start())
    if str == "no":
        await bot.send_message(callback.from_user.id,f"Хотите оставить заявку?",reply_markup=kb_question())

async def on_shutdown(dp):
    logging.warning('Shutting down..')

    # insert code here to run it before shutdown

    # Remove webhook (not acceptable in some cases)
    await bot.delete_webhook()

    # Close DB connection (if used)
    await dp.storage.close()
    await dp.storage.wait_closed()

    logging.warning('Bye!')

def start_webhook(
        dispatcher,
        webhook_path,
        *,
        loop=None,
        skip_updates=None,
        on_startup=None,
        on_shutdown=None,
        check_ip=False,
        retry_after=None,
        route_name=DEFAULT_ROUTE_NAME,
        **kwargs
):
    executor = set_webhook(dispatcher=dispatcher,
                           webhook_path=webhook_path,
                           loop=loop,
                           skip_updates=skip_updates,
                           on_startup=on_startup,
                           on_shutdown=on_shutdown,
                           check_ip=check_ip,
                           retry_after=retry_after,
                           route_name=route_name,
                           web_app=app)
    executor.run_app(**kwargs)

if __name__ == '__main__':
    dp.register_message_handler(start, commands=['start'], state=None)
    dp.register_message_handler(contacts, commands=['contacts'], state=None)
    dp.register_message_handler(city, content_types=['any'], state=Search.city)
    dp.register_message_handler(street, content_types=['any'], state=Search.street)
    #dp.register_message_handler(phone, content_types=['any'], state=Question.phone)
    dp.register_message_handler(question, content_types=['any'], state=Question.q_from_user)

    dp.register_callback_query_handler(welcome_button, Text(startswith='starting'), state=None)
    dp.register_callback_query_handler(quest, Text(startswith='quest_'), state=None)
    dp.register_callback_query_handler(inner, Text(startswith='inner_'), state=None)
    start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )