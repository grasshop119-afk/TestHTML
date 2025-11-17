import os
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Получаем токен из environment variables
TOKEN = os.getenv('TOKEN')
if not TOKEN:
    raise ValueError("Токен бота не найден! Убедись, что переменная TOKEN установлена в Render.")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    keyboard = [
        [InlineKeyboardButton("Открыть приложение", web_app={"url": "https://telegram-web-app-bot-test.glitch.me/"})]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    message_text = f"""🔥 *Привет, {user.first_name}*!

Так как разраб не имеет всей информации о боте, здесь будет стоять эта чертова заглушка. А что поделать?

_Зато ты увидишь как выглядит массивное сообщение!_

⭐️ Круто, да? В душе не чаю! В любом случае, пока здесь эта фигня, бот работает, можно сказать, только наполовину…"""

    await update.message.reply_text(
        message_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

def main():
    # Создаем Application
    application = Application.builder().token(TOKEN).build()
    
    # Добавляем обработчики - ТОЛЬКО СТАРТ
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Запускаем бота
    logging.info("Бот запущен!")
    application.run_polling()

if __name__ == '__main__':
    main()
