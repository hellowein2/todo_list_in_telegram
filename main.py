import telebot
import sqlite3
from datetime import datetime
from telebot import types
from ignore.api import API

API_TOKEN = API

__version__ = 'v.0.6'

bot = telebot.TeleBot(API_TOKEN)


def add_users(message):
    user_id = message.from_user.id
    username = message.from_user.username

    with sqlite3.connect('ignore/data.db') as connection:
        cursor = connection.cursor()

        cursor.execute('''
                CREATE TABLE IF NOT EXISTS Users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT
                )
            ''')
        cursor.execute('INSERT OR REPLACE INTO Users (user_id, username) VALUES (?, ?)'
                       , (user_id, username))

        cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS Tasks{user_id} (
        task TEXT NOT NULL,
        time TEXT NOT NULL
        )
        ''')


def add_task(message, edit_msg):
    kb = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Добавить задачу', callback_data='add_task')
    btn2 = types.InlineKeyboardButton(text='Просмотреть задачи', callback_data='view_tasks')
    kb.add(btn1, btn2)

    with sqlite3.connect('ignore/data.db') as connection:
        cursor = connection.cursor()

        cursor.execute(f'INSERT INTO Tasks{message.from_user.id} (task, time) VALUES (?, ?)',
                       (f'{message.text}', f'{datetime.today().strftime("%d.%m.%Y %H:%M")}'))

    bot.edit_message_text(chat_id=message.from_user.id, text=f'Вы добавили задачу: {message.text}',
                          message_id=edit_msg.message_id,
                          reply_markup=kb)
    bot.delete_message(message.chat.id, message.message_id)


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    kb = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Добавить задачу', callback_data='add_task')
    btn2 = types.InlineKeyboardButton(text='Просмотреть задачи', callback_data='view_tasks')
    kb.add(btn1)
    kb.add(btn2)

    bot.send_message(message.chat.id, f'Ку {message.from_user.first_name} я todo list {__version__}', reply_markup=kb)

    add_users(message)


@bot.callback_query_handler(func=lambda call: call.data == 'back')
def back_to_main(call):
    bot.clear_step_handler_by_chat_id(chat_id=call.message.chat.id)
    kb = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Добавить задачу', callback_data='add_task')
    btn2 = types.InlineKeyboardButton(text='Просмотреть задачи', callback_data='view_tasks')
    kb.add(btn1, btn2)

    bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.message_id,
                          text=f'todo list {__version__}', reply_markup=kb)


@bot.message_handler(content_types=['text'])
def del_message(message):
    bot.delete_message(message.chat.id, message.message_id)


@bot.callback_query_handler(func=lambda call: call.data == 'add_task')
def pre_add_task(call):
    kb = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton(text='Назад', callback_data='back')
    kb.add(btn1)
    edit_msg = bot.edit_message_text(chat_id=call.message.chat.id,
                                     message_id=call.message.message_id,
                                     text='Введите задачу', reply_markup=kb)

    bot.register_next_step_handler(edit_msg, add_task, edit_msg)


@bot.callback_query_handler(func=lambda call: call.data == 'view_tasks')
def view_tasks(call):
    with sqlite3.connect('ignore/data.db') as connection:
        cursor = connection.cursor()
        kb = types.InlineKeyboardMarkup()
        count = []
        task = False
        for i in cursor.execute(f'SELECT rowid, * FROM Tasks{call.message.chat.id}'):
            btn = types.InlineKeyboardButton(text=i[1], callback_data=f'task_id_{i[0]}')
            count.append(btn)
            task = True

        if task:
            kb.add(*count)
            btn = types.InlineKeyboardButton('Назад', callback_data='back')
            kb.add(btn)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text='Ваши задачи:', reply_markup=kb)
        else:
            btn = types.InlineKeyboardButton(text='Добавить задачу', callback_data='add_task')
            kb.add(btn)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text='Задач ещё нет', reply_markup=kb)


@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    if call.data.startswith('task_id_'):
        task_id = call.data.split('_')[2]
        handle_selected_task(call, task_id)
    elif call.data.startswith('delete_task_'):
        task_id = call.data.split('_')[2]
        delete_selected_task(call, task_id)
    elif call.data == 'back':
        back_to_main(call)


def handle_selected_task(call, task_id):
    kb = types.InlineKeyboardMarkup()
    btn1 = types.InlineKeyboardButton('Назад', callback_data='view_tasks')
    btn2 = types.InlineKeyboardButton('Удалить', callback_data=f'delete_task_{task_id}')
    kb.add(btn1, btn2)

    with sqlite3.connect('ignore/data.db') as connection:
        cursor = connection.cursor()

        cursor.execute(f'SELECT * FROM Tasks{call.message.chat.id} WHERE rowid = ?', (task_id,))

        task = cursor.fetchone()

        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=f'{task[0]} - {task[1]}', reply_markup=kb)


def delete_selected_task(call, task_id):
    with sqlite3.connect('ignore/data.db') as connection:
        cursor = connection.cursor()
        cursor.execute(f'DELETE FROM Tasks{call.message.chat.id} WHERE rowid = ?', (task_id,))
    view_tasks(call)


if __name__ == '__main__':
    bot.infinity_polling(skip_pending=True)
