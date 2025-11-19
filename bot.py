import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, CallbackQueryHandler, ContextTypes
import requests

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Токены из переменных окружения Render
TOKEN = os.environ.get('TOKEN')  # Токен Telegram бота
AITOKEN = os.environ.get('AITOKEN')  # Токен Hugging Face

# URL API Hugging Face для DialoGPT-large
HF_API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-large"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик команды /start"""
    user = update.message.from_user
    keyboard = [
        [
            InlineKeyboardButton("Kraken WEB", callback_data="web"),
            InlineKeyboardButton("Промпты", callback_data="prompts")
        ],
        [
            InlineKeyboardButton("Тариф", callback_data="tariff")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        f"Привет, *{user.first_name}*! 🐙\n\n"
        "_Добро пожаловать в Kraken, мы рады тебя здесь видеть! Это текстовый ИИ-бот в Telegram, с кучей удобных возможностей. Попробуй спросить что-нибудь, и я отвечу в течение минуты!_",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик нажатий на инлайн-кнопки"""
    query = update.callback_query
    await query.answer()
    
    # Пока просто отвечаем сообщением
    if query.data == "web":
        await query.edit_message_text("🌐 *Kraken WEB*\n\nСкоро здесь будет ссылка на наш сайт!", parse_mode='Markdown')
    elif query.data == "prompts":
        await query.edit_message_text("📝 *Промпты*\n\nРаздел с промптами в разработке!", parse_mode='Markdown')
    elif query.data == "tariff":
        await query.edit_message_text("💰 *Тариф*\n\nИнформация о тарифах появится позже!", parse_mode='Markdown')

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

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик текстовых сообщений"""
    user_message = update.message.text
    
    # Показываем, что бот печатает
    await update.message.chat.send_action(action="typing")
    
    # Получаем ответ от AI
    ai_response = get_ai_response(user_message)
    
    # Отправляем ответ пользователю
    await update.message.reply_text(ai_response)

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обработчик ошибок"""
    logger.error(f"Update {update} caused error {context.error}")

def main():
    """Основная функция запуска бота"""
    if not TOKEN:
        logger.error("❌ TOKEN environment variable is not set!")
        return
    if not AITOKEN:
        logger.warning("⚠️ AITOKEN environment variable is not set! AI features will not work.")
    
    # Создаем приложение
    application = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчики
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_error_handler(error_handler)
    
    # Запускаем бота
    logger.info("🤖 Бот запущен!")
    application.run_polling()

if __name__ == '__main__':
    main()
