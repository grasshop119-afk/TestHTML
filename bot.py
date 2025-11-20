import telebot
from telebot import types
import requests
import logging
import os
import time

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Токен бота из переменных окружения Render
BOT_TOKEN = os.environ.get('TOKEN')
if not BOT_TOKEN:
    logger.error("❌ TOKEN не установлен!")
    exit(1)

bot = telebot.TeleBot(BOT_TOKEN)

# Токен для Hugging Face AI
HF_TOKEN = os.environ.get('AITOKEN')
if not HF_TOKEN:
    logger.error("❌ AITOKEN не установлен!")
    exit(1)

class RussianAI:
    def __init__(self, hf_token):
        self.hf_token = hf_token
        self.model_name = "sberbank-ai/rugpt3small_based_on_gpt2"
    
    def generate_response(self, message):
        """Генерирует ответ используя Hugging Face API"""
        try:
            # Пробуем разные endpoint'ы
            endpoints = [
                f"https://api-inference.huggingface.co/models/{self.model_name}",
                f"https://router.huggingface.co/models/{self.model_name}",
                f"https://huggingface.co/api/models/{self.model_name}/inference"
            ]
            
            for endpoint in endpoints:
                try:
                    logger.info(f"Пробуем endpoint: {endpoint}")
                    
                    response = requests.post(
                        endpoint,
                        headers={"Authorization": f"Bearer {self.HF_TOKEN}"},
                        json={
                            "inputs": message,
                            "parameters": {
                                "max_length": 100,  # Уменьшаем для скорости
                                "temperature": 0.7,
                                "do_sample": True,
                                "repetition_penalty": 1.1
                            },
                            "options": {
                                "wait_for_model": True,
                                "use_cache": True
                            }
                        },
                        timeout=20
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        if isinstance(result, list) and len(result) > 0:
                            generated_text = result[0].get('generated_text', '')
                            if generated_text.startswith(message):
                                generated_text = generated_text[len(message):].strip()
                            return generated_text if generated_text else "🤔 Нейросеть ответила пустым сообщением"
                        else:
                            continue  # Пробуем следующий endpoint
                    
                    logger.warning(f"Endpoint {endpoint} вернул статус {response.status_code}")
                    
                except requests.exceptions.Timeout:
                    logger.warning(f"Timeout для {endpoint}")
                    continue
                except Exception as e:
                    logger.warning(f"Ошибка в {endpoint}: {e}")
                    continue
            
            # Если все endpoint'ы не сработали, используем fallback
            return self.fallback_response(message)
                
        except Exception as e:
            logger.error(f"Общая ошибка: {e}")
            return self.fallback_response(message)
    
    def fallback_response(self, message):
        """Простой fallback когда API не работает"""
        responses = {
            "привет": "Привет! Я бот с нейросетью. К сожалению, основная нейросеть временно недоступна, но я могу ответить на простые вопросы!",
            "как дела": "У меня всё отлично! Работаю в тестовом режиме. А у тебя?",
            "что ты умеешь": "Я могу общаться на русском языке, но пока использую упрощённые ответы. Нейросеть скоро вернётся!",
            "нейросеть": "Нейросеть временно недоступна. Используются базовые ответы.",
            "кто тебя создал": "Меня создали с помощью Python и Telegram API!",
            "пока": "До свидания! Возвращайся, когда нейросеть заработает!",
            "помощь": "Просто напиши мне сообщение, и я постараюсь ответить. Сейчас работаю в упрощённом режиме."
        }
        
        message_lower = message.lower()
        for key, response in responses.items():
            if key in message_lower:
                return response
        
        # Если нет подходящего ответа
        return "Интересный вопрос! К сожалению, нейросеть временно недоступна. Попробуй спросить что-то другое или зайди позже! 🚀"

# Создаем экземпляр нейросети
ai = RussianAI(HF_TOKEN)

@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = """
🤖 *Добро пожаловать в KrakenBot AI!*

Сейчас я работаю в *упрощённом режиме* (нейросеть временно недоступна), но всё равно могу общаться!

*Команды:*
/start - это сообщение
/help - помощь  
/info - информация
/status - статус нейросети

Просто напиши мне что-нибудь! 😊
    """
    
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn1 = types.KeyboardButton('👋 Привет')
    btn2 = types.KeyboardButton('❓ Помощь')
    btn3 = types.KeyboardButton('🤖 О боте')
    markup.add(btn1, btn2, btn3)
    
    bot.send_message(message.chat.id, welcome_text, 
                     parse_mode='Markdown', reply_markup=markup)

@bot.message_handler(commands=['status'])
def check_status(message):
    """Проверка статуса нейросети"""
    bot.send_chat_action(message.chat.id, 'typing')
    
    # Тестируем нейросеть
    test_result = ai.generate_response("Тест")
    
    if "нейросеть временно недоступна" in test_result.lower():
        status_text = "🔴 *Статус:* Нейросеть временно недоступна\n🟢 *Бот:* Работает в упрощённом режиме"
    else:
        status_text = f"🟢 *Статус:* Нейросеть работает!\n*Тест:* {test_result[:100]}..."
    
    bot.send_message(message.chat.id, status_text, parse_mode='Markdown')

@bot.message_handler(commands=['help', 'info'])
def send_help(message):
    help_text = """
*Помощь и информация:*

🤖 *Текущий режим:* Упрощённый (нейросеть настраивается)
💬 *Общение:* Отвечаю на базовые вопросы
⚡ *Статус:* /status - проверить нейросеть

*Что я могу:*
• Отвечать на простые вопросы
• Общаться на русском
• Работать 24/7

Нейросеть скоро вернётся в полную силу! 🚀
    """
    bot.send_message(message.chat.id, help_text, parse_mode='Markdown')

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    try:
        bot.send_chat_action(message.chat.id, 'typing')
        
        # Обрабатываем кнопки
        if message.text == '👋 Привет':
            user_message = "привет"
        elif message.text == '❓ Помощь':
            user_message = "помощь"
        elif message.text == '🤖 О боте':
            user_message = "что ты умеешь"
        else:
            user_message = message.text
        
        # Получаем ответ
        response = ai.generate_response(user_message)
        
        # Отправляем ответ
        bot.send_message(message.chat.id, response)
        
        logger.info(f"User {message.from_user.id}: {user_message[:30]}...")
        
    except Exception as e:
        logger.error(f"Error: {e}")
        bot.send_message(message.chat.id, "⚠️ Ошибка. Попробуйте еще раз.")

if __name__ == '__main__':
    logger.info("🤖 Бот запускается...")
    
    # Тестируем нейросеть
    try:
        logger.info("🔧 Тестируем нейросеть...")
        test_response = ai.generate_response("Привет")
        logger.info(f"✅ Тест: {test_response[:50]}...")
    except Exception as e:
        logger.error(f"❌ Ошибка теста: {e}")
    
    logger.info("🚀 Бот запущен!")
    
    try:
        bot.infinity_polling(timeout=60, long_polling_timeout=30)
    except Exception as e:
        logger.error(f"💥 Ошибка бота: {e}")
