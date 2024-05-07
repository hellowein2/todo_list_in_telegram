import telebot
import sqlite3
from telebot import types
from datetime import datetime
from ignore.api import API

API_TOKEN = API

bot = telebot.TeleBot(API_TOKEN)


def add_user_data(message):
    global copyblock
    copyblock = True

    username = message.from_user.username
    user_id = message.from_user.id

    connection = sqlite3.connect('ignore/data_users.db')
    cursor = connection.cursor()

    cursor.execute('''
    CREATE TABLE IF NOT EXISTS Users (
    user_id INTEGER,
    username TEXT
    )
    ''')
    # checking for duplicates
    for i in cursor.execute('SELECT user_id FROM Users'):
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
    connection = sqlite3.connect('ignore/data_users.db')
    cursor = connection.cursor()

    cursor.execute(f'INSERT INTO Tasks{message.from_user.id} (task, time) VALUES (?, ?)', (f'{message.text}', f'{datetime.today().strftime("%D %H:%M")}'))

    connection.commit()
    cursor.close()
    connection.close()
    bot.send_message(message.chat.id, 'Задача добавлена!')



def view_tasks(message):
    connection = sqlite3.connect('ignore/data_users.db')
    cursor = connection.cursor()
    task = ''
    count = 0
    for i in cursor.execute(f'SELECT * FROM Tasks{message.from_user.id}'):
        count += 1
        task += f'{count}: {i[0]} {i[1]}\n'
    bot.send_message(message.chat.id, task)

    cursor.close()
    connection.close()

@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Добавить задачу')
    btn2 = types.KeyboardButton('Показать задачи')
    markup.row(btn1, btn2)
    add_user_data(message)
    bot.send_message(message.chat.id, f'Ку {message.from_user.first_name} я todo list v0.0.1', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def send_message(message):
    if message.text == 'Добавить задачу':
        msg = bot.send_message(message.chat.id, 'Введите задачу')
        bot.register_next_step_handler(msg, add_task)
    if message.text == 'Показать задачи':
        view_tasks(message)



bot.infinity_polling()
