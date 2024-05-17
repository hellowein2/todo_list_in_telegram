import telebot
import sqlite3
from telebot import types
from datetime import datetime
from ignore.api import API

API_TOKEN = API

__version__ = 'v.0.1.1'

bot = telebot.TeleBot(API_TOKEN)

global dic_tasks


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
    if message.text == 'Показать задачи':
        view_tasks(message)
    elif message.text == 'Добавить задачу':
        msg = bot.send_message(message.chat.id, 'Введите задачу')
        bot.register_next_step_handler(msg, add_task)
    else:
        connection = sqlite3.connect('ignore/data_users.db')
        cursor = connection.cursor()

        cursor.execute(f'INSERT INTO Tasks{message.from_user.id} (task, time) VALUES (?, ?)',
                       (f'{message.text}', f'{datetime.today().strftime("%Y.%m.%d %H:%M")}'))

        connection.commit()
        cursor.close()
        connection.close()
        bot.send_message(message.chat.id, 'Задача добавлена!')


def view_tasks(message):
    connection = sqlite3.connect('ignore/data_users.db')
    cursor = connection.cursor()

    global kb1
    kb1 = ''

    global exists_task
    exists_task = True

    global count
    count = 0

    global dic_tasks
    dic_tasks = []

    dic = {}
    for i in cursor.execute(f'SELECT * FROM Tasks{message.from_user.id}'):
        count += 1
        kb1 = types.InlineKeyboardMarkup()
        dic["btn" + str(count)] = types.InlineKeyboardButton(text=f'{i[0]}', callback_data=count)
        dic_tasks.append(f'{i[0]}')
        exists_task = False
    if exists_task:
        bot.send_message(message.chat.id, "Задач еще нет!")
    else:
        for i in range(1, count + 1):
            kb1.add(dic[f'btn{i}'])
            connection.commit()

        bot.send_message(message.chat.id, "Вот все ваши задачи", reply_markup=kb1)

    cursor.close()
    connection.close()


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Добавить задачу')
    btn2 = types.KeyboardButton('Показать задачи')
    markup.row(btn1, btn2)
    add_user_data(message)
    bot.send_message(message.chat.id, f'Ку {message.from_user.first_name} я todo list {__version__}', reply_markup=markup)


@bot.message_handler(content_types=['text'])
def send_message(message):
    if message.text == 'Добавить задачу':
        msg = bot.send_message(message.chat.id, 'Введите задачу')
        bot.register_next_step_handler(msg, add_task)
    if message.text == 'Показать задачи':
        view_tasks(message)


@bot.callback_query_handler(func=lambda call: True)
def view_specific_task(call):
    for i in range(1, count + 1):
        if call.data == f'{i}':
            kb1 = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton(text='Удалить', callback_data=f'{dic_tasks[i - 1]}')
            kb1.add(btn1)
            bot.send_message(call.message.chat.id, f'Вы выбрали задачу:   {dic_tasks[i - 1]}', reply_markup=kb1)
            break
        else:
            pass

    for i in range(1, count + 1):
        delete_task = dic_tasks[i - 1]
        if call.data == f'{delete_task}':
            connection = sqlite3.connect('ignore/data_users.db')
            cursor = connection.cursor()

            cursor.execute(f'''SELECT * from Tasks{call.message.chat.id}''')
            cursor.execute(f'DELETE FROM Tasks{call.message.chat.id} WHERE task = "{delete_task}"')

            connection.commit()
            cursor.close()
            connection.close()

            bot.send_message(call.message.chat.id, f'Вы удалили задачу:   {delete_task}')
        else:
            pass


bot.infinity_polling()
