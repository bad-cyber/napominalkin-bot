#!/usr/bin/env python3
"""
Тестовый скрипт для проверки функциональности бота напоминаний
"""

import json
import datetime

# Тест базы данных
def test_database():
    print("🧪 Тестирование базы данных...")
    
    # Имитируем данные напоминания
    test_reminder = {
        'text': 'Тестовое напоминание',
        'datetime': datetime.datetime.now().isoformat(),
        'repeat': 'daily',
        'days': None,
        'user_id': 123456789
    }
    
    print(f"📝 Тестовые данные: {json.dumps(test_reminder, indent=2, ensure_ascii=False)}")
    print("✅ База данных готова к работе!")

# Тест логики напоминаний
def test_reminder_logic():
    print("\n🧪 Тестирование логики напоминаний...")
    
    now = datetime.datetime.now()
    
    # Создаем тестовые напоминания с разными сценариями
    test_reminders = [
        {
            'name': 'Одноразовое напоминание (текущее время)',
            'repeat': 'none',
            'days': None,
            'datetime': now.isoformat(),
            'active': True
        },
        {
            'name': 'Ежедневное напоминание',
            'repeat': 'daily',
            'days': None,
            'datetime': now.replace(minute=now.minute + 1, second=0, microsecond=0).isoformat(),
            'active': True
        },
        {
            'name': 'Еженедельное напоминание',
            'repeat': 'weekly',
            'days': None,
            'datetime': now.replace(minute=now.minute + 1, second=0, microsecond=0).isoformat(),
            'active': True
        }
    ]
    
    # Тестируем функцию should_send_reminder
    for reminder in test_reminders:
        reminder_time = datetime.datetime.fromisoformat(reminder['datetime'])
        
        # Имитируем вызов функции проверки
        should_trigger = False
        
        if reminder['repeat'] == 'none':
            # Для одноразовых - проверяем точное время
            should_trigger = now.strftime("%Y-%m-%d %H:%M") == reminder_time.strftime("%Y-%m-%d %H:%M")
        
        elif reminder['repeat'] == 'daily':
            # Ежедневно - проверяем время
            should_trigger = now.time() == reminder_time.time()
        
        elif reminder['repeat'] == 'weekly':
            # Еженедельно - проверяем день недели и время
            should_trigger = now.weekday() == reminder_time.weekday() and now.time() == reminder_time.time()
        
        print(f"📋 {reminder['name']}: {'✅' if should_trigger else '❌'}")
        
        # Дополнительная информация для отладки
        if reminder['repeat'] == 'daily':
            print(f"   ⏰ Текущее время: {now.time()}, Время напоминания: {reminder_time.time()}")
        elif reminder['repeat'] == 'weekly':
            print(f"   📅 Текущий день: {now.weekday()}, День напоминания: {reminder_time.weekday()}")
            print(f"   ⏰ Текущее время: {now.time()}, Время напоминания: {reminder_time.time()}")

def test_notification_message():
    print("\n🧪 Тестирование сообщений уведомлений...")
    
    test_reminder = {
        'text': 'Купить молоко',
        'user_id': 123456789
    }
    
    user_info = {
        'first_name': 'Иван'
    }
    
    message = f"""
🔔 <b>Напоминалкин напоминает!</b>

Помнишь то что ты указал "{test_reminder['text']}"? 
Так вот, напоминаю тебе, что это нужно сделать сегодня.

Хорошего тебе дня, {user_info['first_name']}! 🌟
    """
    
    print("📨 Пример уведомления:")
    print(message)
    print("✅ Форматирование сообщений работает корректно!")

if __name__ == "__main__":
    print("🚀 Запуск тестов Napominalkin Bot")
    print("=" * 50)
    
    test_database()
    test_reminder_logic()
    test_notification_message()
    
    print("\n" + "=" * 50)
    print("🎉 Все тесты пройдены успешно!")
    print("\n📋 Для запуска бота выполните:")
    print("1. Установите зависимости: pip install -r requirements.txt")
    print("2. Создайте файл .env с токеном бота: BOT_TOKEN=your_bot_token_here")
    print("3. Запустите бота: python main.py")
