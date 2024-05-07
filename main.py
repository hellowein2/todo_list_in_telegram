import telebot
import sqlite3

# # Создаем подключение к базе данных
# connection = sqlite3.connect('data_users.db')
# cursor = connection.cursor()
#
# cursor.execute('''
# CREATE TABLE IF NOT EXISTS Users (
# user_id INTEGER NOT NULL,
# username TEXT NOT NULL
# )
# ''')
# connection.commit()
# connection.close()




API_TOKEN = '6962301596:AAGFJ9IUFDQL62-EcHUAvOBerCGaBsBSOiQ'

bot = telebot.TeleBot(API_TOKEN)


def add_user_data(message):
    username = message.from_user.username
    user_id = message.from_user.id

    connection = sqlite3.connect('data_users.db')
    cursor = connection.cursor()
    cursor.execute('INSERT INTO Users (user_id, username) VALUES (?, ?)', (f'{user_id}', f'{username}'))

    connection.commit()
    connection.close()


@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, 'Ку я todo list v0.0.1')
    add_user_data(message)


bot.infinity_polling()
