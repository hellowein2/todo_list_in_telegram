import telebot
import sqlite3
from telebot import types
from datetime import datetime
from ignore.api import API

API_TOKEN = API

__version__ = 'v.0.2.2'

bot = telebot.TeleBot(API_TOKEN)

global dic_tasks
global edit_msg
global kb1
global exists_task
global count
global copyblock
global msg
check_1 = True


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
    global msg
    if message.text == 'Показать задачи':
        view_tasks(message)
    elif message.text == 'Добавить задачу':
        msg = bot.edit_message_text('Введите задачу', chat_id=message.from_user.id, message_id=msg.message_id)
        bot.register_next_step_handler(msg, add_task)
    else:
        connection = sqlite3.connect('ignore/data_users.db')
        cursor = connection.cursor()
        try:
            cursor.execute(f'INSERT INTO Tasks{message.from_user.id} (task, time) VALUES (?, ?)',
                           (f'{message.text}', f'{datetime.today().strftime("%Y.%m.%d %H:%M")}'))
        except sqlite3.OperationalError:
            add_user_data(message)
            cursor.execute(f'INSERT INTO Tasks{message.from_user.id} (task, time) VALUES (?, ?)',
                           (f'{message.text}', f'{datetime.today().strftime("%Y.%m.%d %H:%M")}'))

        connection.commit()
        cursor.close()
        connection.close()
        msg = bot.edit_message_text('Задача добавлена!', chat_id=message.from_user.id, message_id=msg.message_id)
        bot.delete_message(message.chat.id, message.message_id)


def view_tasks(message, check_back=False):
    connection = sqlite3.connect('ignore/data_users.db')
    cursor = connection.cursor()

    global check_1

    global kb1
    kb1 = ''

    global msg

    global exists_task
    exists_task = True

    global count
    count = 0

    global dic_tasks
    dic_tasks = []

    dic = {}
    try:
        for i in cursor.execute(f'SELECT * FROM Tasks{message.from_user.id}'):
            count += 1
            kb1 = types.InlineKeyboardMarkup()
            dic["btn" + str(count)] = types.InlineKeyboardButton(text=f'{i[0]}', callback_data=count)
            dic_tasks.append(f'{i[0]}')
            exists_task = False
    except sqlite3.OperationalError:
        add_user_data(message)

    if exists_task:
        try:
            bot.edit_message_text(chat_id=message.from_user.id, text="Задач еще нет!", message_id=msg.message_id)
        except:
            pass
    else:
        for i in range(1, count + 1):
            kb1.add(dic[f'btn{i}'])
            connection.commit()

            try:
                bot.edit_message_text(text="Ваши задачи: ", chat_id=message.from_user.id, reply_markup=kb1, message_id=msg.message_id)
            except:
                pass

    cursor.close()
    connection.close()


def check_delete_or_not():
    global check_1
    check_1 = False


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    global msg
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('Добавить задачу')
    btn2 = types.KeyboardButton('Показать задачи')
    markup.row(btn1, btn2)
    add_user_data(message)
    msg = bot.send_message(message.chat.id, f'Ку {message.from_user.first_name} я todo list {__version__}',
                           reply_markup=markup)


@bot.message_handler(content_types=['text'])
def send_message(message):
    global msg
    if message.text == 'Добавить задачу':
        try:
            msg = bot.edit_message_text(chat_id=message.chat.id, text='Введите задачу', message_id=msg.message_id)
        except:
            msg = bot.send_message(chat_id=message.chat.id, text='Введите задачу')

        bot.register_next_step_handler(msg, add_task)
        bot.delete_message(message.chat.id, message.message_id)

    if message.text == 'Показать задачи':
        bot.delete_message(message.chat.id, message.message_id)
        view_tasks(message)


@bot.callback_query_handler(func=lambda call: True)
def view_specific_task(call):
    # view task
    for i in range(1, count + 1):
        if call.data == f'{i}':
            kb2 = types.InlineKeyboardMarkup()
            btn1 = types.InlineKeyboardButton(text='Удалить', callback_data=f'{dic_tasks[i - 1]}delete')
            btn2 = types.InlineKeyboardButton(text='Назад', callback_data='back')
            kb2.add(btn1, btn2)

            connection = sqlite3.connect('ignore/data_users.db')
            cursor = connection.cursor()
            # add time in message
            for y in (cursor.execute(f'SELECT time FROM Tasks{call.message.chat.id}'
                                     f' WHERE task = "{dic_tasks[i - 1]}"')):
                bot.edit_message_text(f'{dic_tasks[i - 1]} - {y[0]}', chat_id=call.message.chat.id, reply_markup=kb2,
                                      message_id=msg.message_id)

            cursor.close()
            connection.close()
            break
        else:
            pass
    # delete task
    for i in range(1, count + 1):
        delete_task = dic_tasks[i - 1]
        if call.data == f'{delete_task}delete':
            connection = sqlite3.connect('ignore/data_users.db')
            cursor = connection.cursor()

            cursor.execute(f'''SELECT * from Tasks{call.message.chat.id}''')
            cursor.execute(f'DELETE FROM Tasks{call.message.chat.id} WHERE task = "{delete_task}"')

            connection.commit()
            cursor.close()
            connection.close()

            bot.edit_message_text(f'Вы удалили задачу:   {delete_task}', chat_id=call.message.chat.id,
                                  message_id=msg.message_id)
            check_delete_or_not()

        else:
            pass

        if call.data == 'back':
            view_tasks(call, check_back=True)


bot.infinity_polling()
