import telebot
import sqlite3
from telebot import types
import datetime

API_TOKEN = '6962301596:AAGFJ9IUFDQL62-EcHUAvOBerCGaBsBSOiQ'

bot = telebot.TeleBot(API_TOKEN)


def add_user_data(message):
    global copyblock
    copyblock = True
    username = message.from_user.username
    user_id = message.from_user.id

    connection = sqlite3.connect('data_users.db')
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
    user_id INTEGER,
    username TEXT
    )
    ''')
    for i in cursor.execute('SELECT user_id FROM Users'):
        print(i[0])
        if message.from_user.id == i[0]:
            copyblock = False
            print('Пользователь уже в базе')
            break
    if copyblock:
        cursor.execute('INSERT INTO Users (user_id, username) VALUES (?, ?)', (f'{user_id}', f'{username}'))

    cursor.execute(f'''
    CREATE TABLE IF NOT EXISTS Tasks{user_id} (
    task TEXT NOT NULL,
    time TEXT NOT NULL
    )
    ''')

    connection.commit()
    cursor.close()
    connection.close()


def add_task(message):
    connection = sqlite3.connect('data_users.db')
    cursor = connection.cursor()

    cursor.execute(f'INSERT INTO Tasks{message.from_user.id} (task, time) VALUES (?, ?)', ('sqSQ', f'{datetime.time}'))


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Добавить задачу')
    markup.row(btn1)
    add_user_data(message)
    bot.send_message(message.chat.id, f'Ку {message.from_user.first_name} я todo list v0.0.1', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def send_message(message):
    if message.text == 'Добавить задачу':
        add_task(message)


bot.infinity_polling()
