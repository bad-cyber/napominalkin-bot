@echo off
echo ================================
echo    Napominalkin Bot - Запуск
echo ================================
echo.

REM Проверяем наличие виртуального окружения
if not exist venv (
    echo Создание виртуального окружения...
    python -m venv venv
)

REM Активируем виртуальное окружение
echo Активация виртуального окружения...
call venv\Scripts\activate.bat

REM Проверяем установлены ли зависимости
echo Проверка зависимостей...
pip install -r requirements.txt

REM Проверяем наличие .env файла
if not exist .env (
    echo.
    echo ⚠️  ВНИМАНИЕ: Файл .env не найден!
    echo.
    echo Создайте файл .env со следующим содержимым:
    echo BOT_TOKEN=your_bot_token_here
    echo.
    echo Где your_bot_token_here - токен вашего бота от @BotFather
    echo.
    pause
    exit /b 1
)

REM Запускаем бота
echo.
echo 🚀 Запуск Napominalkin Bot...
echo.
python main.py

REM Держим окно открытым после завершения
pause
