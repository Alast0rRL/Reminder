import telebot
from telebot import types
import time
import threading
import json

API_TOKEN = '7247463794:AAGAfPNJoxvtzRSvbx3CYlZvGTDq6ubDrMs'
bot = telebot.TeleBot(API_TOKEN)

# Файл для хранения состояния пользователей
STATE_FILE = 'user_states.json'

# Функция для загрузки состояния пользователей из файла
def load_user_states():
    try:
        with open(STATE_FILE, 'r') as f:
            user_states = json.load(f)
            # Проверяем и исправляем структуру данных, если нужно
            for chat_id, state in user_states.items():
                if isinstance(state, bool):
                    user_states[chat_id] = {"state": state, "last_reminder": time.time()}
            return user_states
    except FileNotFoundError:
        return {}

# Функция для сохранения состояния пользователей в файл
def save_user_states():
    with open(STATE_FILE, 'w') as f:
        json.dump(user_states, f)

# Загрузка состояния пользователей при запуске
user_states = load_user_states()

# Функция для отправки напоминания
def send_reminder(chat_id):
    markup = types.InlineKeyboardMarkup()
    button = types.InlineKeyboardButton("Сделал", callback_data="done")
    markup.add(button)
    bot.send_message(chat_id, "Не забудьте о тренировке!", reply_markup=markup)

# Обработчик команды /start
@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user_states[chat_id] = {"state": False, "last_reminder": time.time()}
    save_user_states()
    send_reminder(chat_id)

# Обработчик нажатия на кнопку
@bot.callback_query_handler(func=lambda call: call.data == "done")
def callback_done(call):
    chat_id = call.message.chat.id
    if chat_id not in user_states:
        user_states[chat_id] = {"state": True, "last_reminder": time.time()}
    else:
        user_states[chat_id]["state"] = True
        user_states[chat_id]["last_reminder"] = time.time()
    save_user_states()
    bot.send_message(chat_id, "Отлично, напомню позже")
    threading.Timer(3600, send_reminder, args=[chat_id]).start()

# Функция для периодической проверки состояния пользователей
def check_user_states():
    while True:
        current_time = time.time()
        for chat_id, info in user_states.items():
            if not info["state"] and current_time - info["last_reminder"] >= 3600:
                send_reminder(chat_id)
                user_states[chat_id]["last_reminder"] = current_time
        save_user_states()
        time.sleep(3600)  # Проверка каждые 3600 секунд (1 час)

# Запуск проверки состояния пользователей в отдельном потоке
threading.Thread(target=check_user_states).start()

# Запуск бота
bot.polling(none_stop=True)
