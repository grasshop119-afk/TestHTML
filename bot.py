import os
import telebot
from telebot import types

# Получаем токен из environment variables
TOKEN = os.getenv('TOKEN')
bot = telebot.TeleBot(TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = message.from_user
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(
        text="Открыть приложение",
        web_app=types.WebAppInfo(url="https://your-username.github.io/your-repo")
    )
    keyboard.add(button)
    
    welcome_text = f"""🔥 *Привет, {user.first_name}*!

Так как разраб не имеет всей информации о боте, здесь будет стоять эта чертова заглушка. А что поделать?

_Зато ты увидишь как выглядит массивное сообщение!_

⭐️ Круто, да? В душе не чаю! В любом случае, пока здесь эта фигня, бот работает, можно сказать, только наполовину…"""
    
    bot.send_message(
        message.chat.id,
        welcome_text,
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

if __name__ == '__main__':
    print("Бот запущен!")
    bot.infinity_polling()
