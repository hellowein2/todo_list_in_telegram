import telebot
import sqlite3

# Создаем подключение к базе данных
connection = sqlite3.connect('data_users.db')
cursor = connection.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS Users (
id TEXT NOT NULL,
username TEXT NOT NULL
)
''')
connection.commit()
connection.close()




API_TOKEN = '6962301596:AAGFJ9IUFDQL62-EcHUAvOBerCGaBsBSOiQ'

bot = telebot.TeleBot(API_TOKEN)


def add_user_data(message):
    connection = sqlite3.connect('data_users.db')
    cursor = connection.cursor()
    cursor.execute('INSERT INTO Users (username, id) VALUES (?, ?)', ('newuser', '@helloweim'))
    print(message.from_user.username)
    connection.commit()
    connection.close()

# Handle '/start' and '/help'
@bot.message_handler(commands=['help', 'start'])
def send_welcome(message):
    bot.reply_to(message, 'Ку я todo list v0.0.1')
    add_user_data(message)


@bot.message_handler(func=lambda message: True)
def echo_message(message):
    bot.reply_to(message, message.text)


bot.infinity_polling()
