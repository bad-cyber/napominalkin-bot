import os
import logging
import asyncio
import json
import datetime
import aioschedule as schedule
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота
bot = Bot(token=os.getenv('BOT_TOKEN'), default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()

# База данных (в реальном проекте используйте PostgreSQL или другую БД)
class Database:
    def __init__(self):
        self.reminders_file = 'reminders.json'
        self.users_file = 'users.json'
        self.load_data()
    
    def load_data(self):
        try:
            with open(self.reminders_file, 'r', encoding='utf-8') as f:
                self.reminders = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.reminders = []
        
        try:
            with open(self.users_file, 'r', encoding='utf-8') as f:
                self.users = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.users = {}
    
    def save_reminders(self):
        with open(self.reminders_file, 'w', encoding='utf-8') as f:
            json.dump(self.reminders, f, ensure_ascii=False, indent=2)
    
    def save_users(self):
        with open(self.users_file, 'w', encoding='utf-8') as f:
            json.dump(self.users, f, ensure_ascii=False, indent=2)
    
    def add_user(self, user_id, username, first_name):
        if str(user_id) not in self.users:
            self.users[str(user_id)] = {
                'username': username,
                'first_name': first_name,
                'registered_at': datetime.datetime.now().isoformat()
            }
            self.save_users()
    
    def add_reminder(self, reminder_data):
        reminder_data['id'] = len(self.reminders) + 1
        reminder_data['created_at'] = datetime.datetime.now().isoformat()
        reminder_data['active'] = True
        self.reminders.append(reminder_data)
        self.save_reminders()
        return reminder_data
    
    def get_user_reminders(self, user_id):
        return [r for r in self.reminders if r.get('user_id') == user_id and r.get('active', True)]
    
    def delete_reminder(self, reminder_id, user_id):
        self.reminders = [r for r in self.reminders if not (r['id'] == reminder_id and r.get('user_id') == user_id)]
        self.save_reminders()
    
    def toggle_reminder(self, reminder_id, user_id):
        for reminder in self.reminders:
            if reminder['id'] == reminder_id and reminder.get('user_id') == user_id:
                reminder['active'] = not reminder.get('active', True)
                self.save_reminders()
                return reminder['active']
        return None

db = Database()

# Клавиатура с Web App кнопкой
def get_main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📱 Открыть приложение", web_app=WebAppInfo(url="https://bad-cyber.github.io/napominalkin-bot/code.html"))],
            [KeyboardButton(text="📋 Мои напоминания"), KeyboardButton(text="❓ Помощь")]
        ],
        resize_keyboard=True
    )
    return keyboard

# Команда старта
@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    first_name = message.from_user.first_name
    
    db.add_user(user_id, username, first_name)
    
    welcome_text = f"""
👋 Привет, {first_name}!

Я — Напоминалкин, твой личный помощник для напоминаний!

✨ Возможности:
• Создание напоминаний с красивым интерфейсом
• Повторяющиеся напоминания (ежедневно, еженедельно, выборочные дни)
• Просмотр всех активных напоминаний
• Уведомления в назначенное время

📱 Нажми кнопку ниже, чтобы открыть приложение и создать своё первое напоминание!
    """
    
    await message.answer(welcome_text, reply_markup=get_main_keyboard())

# Команда помощи
@dp.message(Command("help"))
@dp.message(F.text == "❓ Помощь")
async def cmd_help(message: types.Message):
    help_text = """
🤖 <b>Напоминалкин - Бот Напоминаний</b>

<b>Основные команды:</b>
/start - Начать работу с ботом
/help - Показать эту справку
/my_reminders - Показать мои напоминания

<b>Как использовать:</b>
1. Нажмите кнопку "📱 Открыть приложение"
2. Создайте напоминание через красивый интерфейс
3. Выберите дату, время и тип повторения
4. Бот пришлёт уведомление в нужное время!

<b>Типы повторения:</b>
• Один раз - стандартное напоминание
• Ежедневно - каждый день в это время
• Еженедельно - каждую неделю в этот день и время
• Выбрать дни - конкретные дни недели

💡 <i>Напоминания работают даже если бот был перезапущен!</i>
    """
    await message.answer(help_text, parse_mode=ParseMode.HTML)

# Показать напоминания пользователя
@dp.message(Command("my_reminders"))
@dp.message(F.text == "📋 Мои напоминания")
async def show_reminders(message: types.Message):
    user_id = message.from_user.id
    reminders = db.get_user_reminders(user_id)
    
    if not reminders:
        await message.answer("📭 У вас пока нет активных напоминаний!\n\nНажмите кнопку '📱 Открыть приложение' чтобы создать первое напоминание.")
        return
    
    text = "📋 <b>Ваши напоминания:</b>\n\n"
    
    for reminder in reminders[:10]:  # Ограничиваем показ 10 напоминаниями
        dt = datetime.datetime.fromisoformat(reminder['datetime'])
        formatted_date = dt.strftime("%d.%m.%Y")
        formatted_time = dt.strftime("%H:%M")
        
        repeat_text = ""
        if reminder['repeat'] == 'daily':
            repeat_text = "🔄 Ежедневно"
        elif reminder['repeat'] == 'weekly':
            repeat_text = "📅 Еженедельно"
        elif reminder['repeat'] == 'custom' and reminder.get('days'):
            day_names = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']
            days = [day_names[d] for d in reminder['days']]
            repeat_text = f"📌 По дням: {', '.join(days)}"
        else:
            repeat_text = "⏰ Один раз"
        
        status = "✅ Активно" if reminder.get('active', True) else "⏸️ Приостановлено"
        
        text += f"""
📝 <b>{reminder['text']}</b>
📅 {formatted_date} ⏰ {formatted_time}
{repeat_text}
{status}
🔹 ID: {reminder['id']}
        """
        
        # Добавляем кнопки управления
        builder = InlineKeyboardBuilder()
        if reminder.get('active', True):
            builder.button(text="⏸️ Приостановить", callback_data=f"toggle_{reminder['id']}")
        else:
            builder.button(text="▶️ Возобновить", callback_data=f"toggle_{reminder['id']}")
        builder.button(text="🗑️ Удалить", callback_data=f"delete_{reminder['id']}")
        builder.adjust(2)
        
        await message.answer(text, parse_mode=ParseMode.HTML, reply_markup=builder.as_markup())
        text = ""  # Сбрасываем текст для следующего сообщения
    
    if len(reminders) > 10:
        await message.answer(f"📖 И ещё {len(reminders) - 10} напоминаний...\nИспользуйте приложение для полного просмотра.")

# Обработка callback от кнопок
@dp.callback_query(F.data.startswith("toggle_"))
async def toggle_reminder(callback: types.CallbackQuery):
    reminder_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    
    new_state = db.toggle_reminder(reminder_id, user_id)
    
    if new_state is not None:
        status = "активно" if new_state else "приостановлено"
        await callback.answer(f"Напоминание {status}!")
        await callback.message.edit_reply_markup(reply_markup=None)
        await callback.message.answer(f"✅ Статус напоминания изменен: {'✅ Активно' if new_state else '⏸️ Приостановлено'}")
    else:
        await callback.answer("Напоминание не найдено!")

@dp.callback_query(F.data.startswith("delete_"))
async def delete_reminder(callback: types.CallbackQuery):
    reminder_id = int(callback.data.split("_")[1])
    user_id = callback.from_user.id
    
    db.delete_reminder(reminder_id, user_id)
    
    await callback.answer("Напоминание удалено!")
    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("🗑️ Напоминание успешно удалено!")

# Обработка данных из Web App
@dp.message(F.web_app_data)
async def handle_web_app_data(message: types.Message):
    try:
        data = json.loads(message.web_app_data.data)
        user_id = message.from_user.id
        
        # Добавляем user_id к данным напоминания
        data['user_id'] = user_id
        
        # Преобразуем datetime в правильный формат
        reminder_datetime = datetime.datetime.fromisoformat(data['datetime'].replace('Z', '+00:00'))
        data['datetime'] = reminder_datetime.isoformat()
        
        # Добавляем напоминание в базу
        reminder = db.add_reminder(data)
        
        # Формируем текст подтверждения
        dt = reminder_datetime
        formatted_date = dt.strftime("%d.%m.%Y")
        formatted_time = dt.strftime("%H:%M")
        
        repeat_text = ""
        if data['repeat'] == 'daily':
            repeat_text = "🔄 Ежедневно"
        elif data['repeat'] == 'weekly':
            repeat_text = "📅 Еженедельно"
        elif data['repeat'] == 'custom' and data.get('days'):
            day_names = ['Вс', 'Пн', 'Вт', 'Ср', 'Чт', 'Пт', 'Сб']
            days = [day_names[d] for d in data['days']]
            repeat_text = f"📌 По дням: {', '.join(days)}"
        else:
            repeat_text = "⏰ Один раз"
        
        confirmation_text = f"""
✅ <b>Напоминание создано!</b>

📝 <b>Текст:</b> {data['text']}
📅 <b>Дата:</b> {formatted_date}
⏰ <b>Время:</b> {formatted_time}
🔄 <b>Повторение:</b> {repeat_text}

💡 Бот пришлёт уведомление в назначенное время!
        """
        
        await message.answer(confirmation_text, parse_mode=ParseMode.HTML)
        
    except Exception as e:
        logger.error(f"Error processing web app data: {e}")
        await message.answer("❌ Произошла ошибка при создании напоминания. Попробуйте ещё раз.")

# Функции для планировщика напоминаний
async def check_reminders():
    """Проверяет и отправляет напоминания"""
    now = datetime.datetime.now()
    
    for reminder in db.reminders:
        if not reminder.get('active', True):
            continue
            
        reminder_time = datetime.datetime.fromisoformat(reminder['datetime'])
        user_id = reminder.get('user_id')
        
        if should_send_reminder(now, reminder_time, reminder):
            await send_reminder_notification(user_id, reminder)
            
            # Для одноразовых напоминаний отключаем после отправки
            if reminder.get('repeat') == 'none':
                reminder['active'] = False
                db.save_reminders()

def should_send_reminder(now, reminder_time, reminder):
    """Определяет, нужно ли отправлять напоминание"""
    if reminder.get('repeat') == 'none':
        # Для одноразовых - проверяем точное время
        return now.strftime("%Y-%m-%d %H:%M") == reminder_time.strftime("%Y-%m-%d %H:%M")
    
    elif reminder.get('repeat') == 'daily':
        # Ежедневно - проверяем время
        return now.time() == reminder_time.time()
    
    elif reminder.get('repeat') == 'weekly':
        # Еженедельно - проверяем день недели и время
        return now.weekday() == reminder_time.weekday() and now.time() == reminder_time.time()
    
    elif reminder.get('repeat') == 'custom' and reminder.get('days'):
        # Выбранные дни - проверяем день недели и время
        return now.weekday() in reminder['days'] and now.time() == reminder_time.time()
    
    return False

async def send_reminder_notification(user_id, reminder):
    """Отправляет уведомление о напоминании"""
    try:
        user = db.users.get(str(user_id), {})
        username = user.get('first_name', 'Друг')
        
        message_text = f"""
🔔 <b>Напоминалкин напоминает!</b>

Помнишь то что ты указал "{reminder['text']}"? 
Так вот, напоминаю тебе, что это нужно сделать сегодня.

Хорошего тебе дня, {username}! 🌟
        """
        
        await bot.send_message(user_id, message_text, parse_mode=ParseMode.HTML)
        logger.info(f"Sent reminder to user {user_id}: {reminder['text']}")
        
    except Exception as e:
        logger.error(f"Error sending reminder to user {user_id}: {e}")

# Настройка планировщика
async def scheduler():
    """Запускает планировщик напоминаний"""
    schedule.every().minute.do(check_reminders)
    
    while True:
        await schedule.run_pending()
        await asyncio.sleep(1)

# Запуск бота
async def main():
    logger.info("Starting Napominalkin Bot...")
    
    # Запускаем планировщик в фоне
    asyncio.create_task(scheduler())
    
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
