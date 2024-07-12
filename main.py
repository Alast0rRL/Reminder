import telebot
from telebot import types
from datetime import datetime, timedelta
import threading

class ReminderBot:
    def __init__(self, token):
        self.bot = telebot.TeleBot(token)
        self.user_tasks = {}

        @self.bot.message_handler(commands=['start'])
        def start_handler(message):
            self.bot.send_message(message.chat.id, 'Привет! Я напоминалка-бот. Используй команды для создания напоминаний: /add_cardio, /add_strength, /add_stretching.')

        @self.bot.callback_query_handler(func=lambda call: call.data.startswith("done"))
        def callback_handler(call):
            self.handle_done(call)

    def send_reminder(self, chat_id, reminder_text):
        """
        Функция для отправки напоминания пользователю.
        """
        keyboard = types.InlineKeyboardMarkup()
        done_button = types.InlineKeyboardButton(text="Сделал", callback_data=f"done:{chat_id}")
        keyboard.add(done_button)

        message = self.bot.send_message(chat_id, text=reminder_text, reply_markup=keyboard)
        self.user_tasks[chat_id] = message.message_id

        threading.Timer(60, self.check_reminder, args=[chat_id, message.message_id, reminder_text]).start()

    def check_reminder(self, chat_id, message_id, reminder_text):
        """
        Функция для проверки, была ли нажата кнопка "Сделал".
        """
        if self.user_tasks.get(chat_id) == message_id:
            self.bot.send_message(chat_id, text=f"Не забудь: {reminder_text}")
            threading.Timer(60, self.check_reminder, args=[chat_id, message_id, reminder_text]).start()

    def schedule_reminders(self, chat_id, reminder_text, interval_minutes=15):
        """
        Функция для планирования регулярных напоминаний каждые interval_minutes минут.
        """
        def schedule():
            self.send_reminder(chat_id, reminder_text)
            threading.Timer(interval_minutes * 60, schedule).start()

        schedule()

    def handle_done(self, call):
        """
        Обработчик нажатий на кнопку "Сделал".
        """
        chat_id = int(call.data.split(':')[1])
        self.bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id, text="Отлично! Напоминание перенесено на 15 минут.")
        self.user_tasks.pop(chat_id, None)

    def start_polling(self):
        """
        Запуск бота.
        """
        self.bot.polling(none_stop=True)

# Использование
if __name__ == '__main__':
    TOKEN = '7247463794:AAGAfPNJoxvtzRSvbx3CYlZvGTDq6ubDrMs'
    reminder_bot = ReminderBot(TOKEN)

    # Пример добавления новых тренировок
    @reminder_bot.bot.message_handler(commands=['add_hands'])
    def add_cardio_handler(message):
        chat_id = message.chat.id
        reminder_text = "Пора на кардио тренировку!"
        reminder_bot.schedule_reminders(chat_id, reminder_text, interval_minutes=30)
        reminder_bot.bot.send_message(chat_id, 'Hands тренировка добавлена! Напоминания будут приходить каждые 60 минут.')

    @reminder_bot.bot.message_handler(commands=['add_strength'])
    def add_strength_handler(message):
        chat_id = message.chat.id
        reminder_text = "Пора на силовую тренировку!"
        reminder_bot.schedule_reminders(chat_id, reminder_text, interval_minutes=60)
        reminder_bot.bot.send_message(chat_id, 'Силовая тренировка добавлена! Напоминания будут приходить каждые 60 минут.')

    @reminder_bot.bot.message_handler(commands=['add_stretching'])
    def add_stretching_handler(message):
        chat_id = message.chat.id
        reminder_text = "Пора на растяжку!"
        reminder_bot.schedule_reminders(chat_id, reminder_text, interval_minutes=45)
        reminder_bot.bot.send_message(chat_id, 'Растяжка добавлена! Напоминания будут приходить каждые 45 минут.')

    reminder_bot.start_polling()
