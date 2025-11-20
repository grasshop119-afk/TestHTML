import telebot
from telebot import types
import requests
import json
import logging
import os

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота из переменных окружения Render
BOT_TOKEN = os.environ.get('TOKEN')
if not BOT_TOKEN:
    logger.error("❌ TOKEN не установлен! Добавь его в Environment Variables на Render")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

# Токен для Hugging Face AI
HF_TOKEN = os.environ.get('AITOKEN')
if not HF_TOKEN:
    logger.error("❌ AITOKEN не установлен! Добавь его в Environment Variables")
    exit(1)

class RussianAI:
    def __init__(self, hf_token):
        self.hf_token = hf_token
        self.model_name = "sberbank-ai/rugpt3small_based_on_gpt2"
    
    def generate_response(self, message):
        """Генерирует ответ используя новый Hugging Face API"""
        try:
            # НОВЫЙ URL API
            url = f"https://router.huggingface.co/hf-inference/models/{self.model_name}"
            
            response = requests.post(
                url,
                headers={"Authorization": f"Bearer {self.hf_token}"},
                json={
                    "inputs": message,
                    "parameters": {
                        "max_length": 150,
                        "temperature": 0.7,
                        "do_sample": True,
                        "repetition_penalty": 1.2
                    }
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                if isinstance(result, list) and len(result) > 0:
                    generated_text = result[0].get('generated_text', '')
                    # Убираем повторение промпта
                    if generated_text.startswith(message):
                        generated_text = generated_text[len(message):].strip()
                    return generated_text if generated_text else "🤔 Не удалось сгенерировать ответ"
                else:
                    return "🔄 Модель загружается... попробуйте через минуту"
            else:
                logger.error(f"API Error {response.status_code}: {response.text}")
                return "⚠️ Сервис временно недоступен. Попробуйте позже или задайте другой вопрос."
                
        except requests.exceptions.Timeout:
            return "⏰ Время ожидания ответа истекло. Попробуйте еще раз."
        except Exception as e:
            logger.error(f"Error: {e}")
            return "❌ Произошла ошибка при обработке запроса"

# Создаем экземпляр нейросети
ai = RussianAI(HF_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    """Обработчик команды /start"""
    welcome_text = """
🤖 *Добро пожаловать в KrakenBot AI!*

Я - нейросеть, которая понимает и отвечает на русском языке. Просто напиши мне сообщение, и я постараюсь дать осмысленный ответ!

*Доступные команды:*
/start - показать это сообщение
/help - помощь
/info - информация о боте
/test - проверить работу нейросети

*Примеры вопросов:*
• Расскажи что-нибудь интересное
• Напиши короткий рассказ
• Объясни сложную тему простыми словами
    """
    
    # Создаем клавиатуру
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('🎲 Случайный факт')
    btn2 = types.KeyboardButton('📚 Расскажи историю')
    btn3 = types.KeyboardButton('🤔 Объясни что-то')
    markup.add(btn1, btn2, btn3)
    
    bot.send_message(message.chat.id, welcome_text, 
                     parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(commands=['help'])
def send_help(message):
    """Обработчик команды /help"""
    help_text = """
*Помощь по использованию бота:*

💬 *Просто общение* - напиши любой вопрос или фразу
🎯 *Конкретные запросы* - чем конкретнее вопрос, тем лучше ответ
📝 *Творческие задачи* - попроси написать рассказ, стих или идею

*Советы:*
• Задавай вопросы на русском языке
• Будь конкретен в формулировках
• Если ответ не понравился - перефразируй вопрос

*Примеры:*
"Расскажи о космосе"
"Напиши короткий детективный рассказ" 
"Объясни, что такое искусственный интеллект"
    """
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

@bot.message_handler(commands=['info'])
def send_info(message):
    """Обработчик команды /info"""
    info_text = """
*Информация о боте:*

🧠 *Модель:* ruGPT-3 Small (SberBank)
🔧 *Технологии:* Python, Hugging Face, PyTelegramBotAPI
👨‍💻 *Разработчик:* KrakenBot AI Team
🌐 *Язык:* Русский

Бот использует нейросеть для генерации текстов на русском языке. Ответы создаются искусственным интеллектом и могут содержать неточности.
    """
    bot.send_message(message.chat.id, info_text, parse_mode='Markdown')

@bot.message_handler(commands=['test'])
def test_ai(message):
    """Проверка работы нейросети"""
    bot.send_chat_action(message.chat.id, 'typing')
    
    test_response = ai.generate_response("Привет! Ответь коротко, что ты умеешь?")
    bot.send_message(message.chat.id, f"*Тест нейросети:*\n{test_response}", parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    """Обработчик всех текстовых сообщений"""
    try:
        # Показываем, что бот печатает
        bot.send_chat_action(message.chat.id, 'typing')
        
        # Обрабатываем кнопки быстрых ответов
        if message.text == '🎲 Случайный факт':
            user_message = "Расскажи интересный научный факт"
        elif message.text == '📚 Расскажи историю':
            user_message = "Напиши короткую интересную историю"
        elif message.text == '🤔 Объясни что-то':
            user_message = "Объясни простыми словами что такое искусственный интеллект"
        else:
            user_message = message.text
        
        # Генерируем ответ через нейросеть
        response = ai.generate_response(user_message)
        
        # Отправляем ответ
        bot.send_message(message.chat.id, response)
        
        # Логируем успешный запрос
        logger.info(f"User {message.from_user.id}: {user_message[:50]}...")
        
    except Exception as e:
        logger.error(f"Error handling message: {e}")
        bot.send_message(message.chat.id, "⚠️ Произошла ошибка. Попробуйте еще раз.")

if __name__ == '__main__':
    logger.info("🤖 Бот запускается...")
    
    # Проверяем доступность модели
    try:
        logger.info("🔧 Проверяем работу нейросети...")
        test_response = ai.generate_response("Тестовое сообщение")
        logger.info(f"✅ Тест модели: {test_response[:50]}...")
    except Exception as e:
        logger.error(f"❌ Модель недоступна: {e}")
    
    logger.info("🚀 Бот начал работу!")
    
    # Запускаем бота
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=30)
    except Exception as e:
        logger.error(f"💥 Ошибка запуска бота: {e}")
