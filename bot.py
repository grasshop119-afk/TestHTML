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

# Токены из переменных окружения Render
TOKEN = os.environ.get('TOKEN')  # Токен Telegram бота
AITOKEN = os.environ.get('AITOKEN')  # Токен Hugging Face

bot = telebot.TeleBot(TOKEN)

# URL API Hugging Face для DialoGPT-large
HF_API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large"

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
    
    payload = {
        "inputs": user_message,
        "parameters": {
            "max_new_tokens": 150,
            "temperature": 0.7,
            "do_sample": True,
            "top_p": 0.9
        }
    }
    
    try:
        response = requests.post(HF_API_URL, headers=headers, json=payload, timeout=60)
        result = response.json()
        
        logger.info(f"HF API Response: {result}")
        
        # Обработка разных форматов ответа HF
        if isinstance(result, list) and len(result) > 0:
            if 'generated_text' in result[0]:
                return result[0]['generated_text']
            else:
                return str(result[0])  # На случай другого формата
        
        elif isinstance(result, dict):
            if 'error' in result:
                if 'loading' in result['error']:
                    estimated_time = result.get('estimated_time', 30)
                    return f"🔄 Модель загружается... Попробуйте через {int(estimated_time)} секунд"
                else:
                    return f"❌ Ошибка AI: {result['error']}"
            elif 'generated_text' in result:
                return result['generated_text']
        
        return "🤔 Не удалось обработать ответ AI"
        
    except requests.exceptions.Timeout:
        return "⏰ Время ожидания истекло. Модель всё ещё загружается. Попробуйте через 30 секунд."
    except Exception as e:
        logger.error(f"AI request error: {e}")
        return f"❌ Ошибка соединения с AI: {str(e)}"

@bot.message_handler(func=lambda message: True)
def handle_all_messages(message):
    """Обработчик всех текстовых сообщений"""
    try:
        # Показываем, что бот печатает
        bot.send_chat_action(message.chat.id, 'typing')
        
        # Получаем ответ от AI
        ai_response = get_ai_response(message.text)
        
        # Отправляем ответ пользователю
        bot.reply_to(message, ai_response)
        
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        bot.reply_to(message, "❌ Произошла ошибка при обработке сообщения")

if __name__ == '__main__':
    logger.info("🤖 Бот запущен!")
    bot.infinity_polling()
