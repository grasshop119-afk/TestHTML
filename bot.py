import os
import logging
import requests
import telebot
from telebot import types

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

TOKEN = os.environ.get('TOKEN')
AITOKEN = os.environ.get('AITOKEN')

bot = telebot.TeleBot(TOKEN)

# Пробуем разные модели
MODELS = [
    "microsoft/DialoGPT-medium",  # Более легкая версия
    "microsoft/DialoGPT-small",   # Самая легкая
    "facebook/blenderbot-400M-distill",  # Альтернатива для чатов
]

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Обработчик команды /start"""
    user = message.from_user
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    
    btn_web = types.InlineKeyboardButton("Kraken WEB", callback_data="web")
    btn_prompts = types.InlineKeyboardButton("Промпты", callback_data="prompts")
    btn_tariff = types.InlineKeyboardButton("Тариф", callback_data="tariff")
    
    keyboard.add(btn_web, btn_prompts)
    keyboard.add(btn_tariff)
    
    bot.send_message(
        message.chat.id,
        f"Привет, *{user.first_name}*! 🐙\n\n"
        "_Добро пожаловать в Kraken, мы рады тебя здесь видеть! Это текстовый ИИ-бот в Telegram, с кучей удобных возможностей. Попробуй спросить что-нибудь, и я отвечу в течение минуты!_",
        reply_markup=keyboard,
        parse_mode='Markdown'
    )

@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    """Обработчик нажатий на инлайн-кнопки"""
    if call.data == "web":
        bot.edit_message_text(
            "🌐 *Kraken WEB*\n\nСкоро здесь будет ссылка на наш сайт!",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )
    elif call.data == "prompts":
        bot.edit_message_text(
            "📝 *Промпты*\n\nРаздел с промптами в разработке!",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )
    elif call.data == "tariff":
        bot.edit_message_text(
            "💰 *Тариф*\n\nИнформация о тарифах появится позже!",
            call.message.chat.id,
            call.message.message_id,
            parse_mode='Markdown'
        )

def get_ai_response(user_message):
    """Получение ответа от Hugging Face AI"""
    if not AITOKEN:
        return "❌ Ошибка: AI токен не настроен"
    
    headers = {"Authorization": f"Bearer {AITOKEN}"}
    
    # Пробуем разные модели по очереди
    for model in MODELS:
        try:
            API_URL = f"https://router.huggingface.co/hf-inference/models/{model}"
            
            payload = {
                "inputs": user_message,
                "parameters": {
                    "max_new_tokens": 100,
                    "temperature": 0.7,
                }
            }
            
            response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                if 'generated_text' in result[0]:
                    return result[0]['generated_text']
            
        except Exception as e:
            logger.warning(f"Model {model} failed: {e}")
            continue
    
    return "🤔 Временно недоступно. Попробуйте позже."

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    """Обработчик всех текстовых сообщений"""
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        ai_response = get_ai_response(message.text)
        bot.reply_to(message, ai_response)
        
    except Exception as e:
        logger.error(f"Error: {e}")
        bot.reply_to(message, "❌ Ошибка. Попробуйте еще раз.")

if __name__ == '__main__':
    logger.info("🤖 Бот запущен!")
    bot.infinity_polling()
