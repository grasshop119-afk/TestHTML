import os
import telebot
from telebot import types
import json

TOKEN = os.getenv('TOKEN')
bot = telebot.TeleBot(TOKEN)

user_orders = {}

@bot.message_handler(commands=['start'])
def send_welcome(message):
    user = message.from_user
    keyboard = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton(
        text="Открыть приложение",
        web_app=types.WebAppInfo(url="https://grasshop119-afk.github.io/BestApp-Web/")
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

@bot.message_handler(content_types=['web_app_data'])
def handle_web_app_data(message):
    try:
        data = json.loads(message.web_app_data.data)
        
        if data.get('action') == 'checkout':
            user_orders[message.chat.id] = {
                'order_text': data.get('orderText'),
                'total': data.get('total')
            }
            
            keyboard = types.InlineKeyboardMarkup()
            keyboard.row(
                types.InlineKeyboardButton("Выбрать способ оплаты", callback_data="choose_payment"),
                types.InlineKeyboardButton("Отменить", callback_data="cancel_order")
            )
            
            bot.send_message(
                message.chat.id,
                data.get('orderText'),
                reply_markup=keyboard,
                parse_mode='Markdown'
            )
            
    except Exception as e:
        print(f"Error handling web app data: {e}")

@bot.callback_query_handler(func=lambda call: True)
def handle_callbacks(call):
    if call.data == "choose_payment":
        keyboard = types.InlineKeyboardMarkup()
        keyboard.row(
            types.InlineKeyboardButton("Example 1", callback_data="payment_1"),
            types.InlineKeyboardButton("Example 2", callback_data="payment_2")
        )
        keyboard.row(
            types.InlineKeyboardButton("Example 3", callback_data="payment_3")
        )
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="🔥 *Конечно! Вот, как можно оплатить заказ*\n_Выберите наиболее удобный способ!_",
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        
    elif call.data == "cancel_order":
        # Отправляем команду на закрытие мини-приложения
        bot.send_message(
            call.message.chat.id,
            "Заказ отменен. Мини-приложение закроется автоматически."
        )
        
        # Здесь должен быть код для закрытия мини-приложения
        # В реальности это делается через отправку специального сообщения
        
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="❌ *Заказ отменен*",
            parse_mode='Markdown'
        )
        
    elif call.data.startswith("payment_"):
        bot.edit_message_text(
            chat_id=call.message.chat.id,
            message_id=call.message.message_id,
            text="✅ *Оплата принята!*\nСпасибо за заказ!",
            parse_mode='Markdown'
        )

if __name__ == '__main__':
    print("Бот запущен!")
    bot.infinity_polling()
