@echo off
echo ========================================
echo    Napominalkin Bot Deployment Script
echo ========================================
echo.

REM Проверяем наличие параметров
if "%1"=="" (
    echo ❌ Укажите IP адрес сервера: deploy.bat server_ip
    echo.
    pause
    exit /b 1
)

set SERVER_IP=%1
set SSH_USER=%2
if "%SSH_USER%"=="" set SSH_USER=napominalkin
set APP_DIR=/home/%SSH_USER%/napominalkin-bot

echo 📋 Целевой сервер: %SERVER_IP%
echo 👤 Пользователь: %SSH_USER%
echo 📁 Директория: %APP_DIR%
echo.

echo 🔗 Проверяем подключение к серверу...
ssh %SSH_USER%@%SERVER_IP% "echo Подключение успешно!"
if errorlevel 1 (
    echo ❌ Не удалось подключиться к серверу
    echo.
    pause
    exit /b 1
)

echo 📁 Создаем рабочую директорию...
ssh %SSH_USER%@%SERVER_IP% "mkdir -p %APP_DIR%"

echo 📤 Копируем файлы на сервер...
scp -r .\* %SSH_USER%@%SERVER_IP%:%APP_DIR%/

echo 🐳 Проверяем наличие Docker...
ssh %SSH_USER%@%SERVER_IP% "command -v docker"
if errorlevel 1 (
    echo 📦 Устанавливаем Docker...
    ssh %SSH_USER%@%SERVER_IP% << "EOF"
        sudo apt update
        sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
        sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
        sudo apt update
        sudo apt install -y docker-ce docker-ce-cli containerd.io
        sudo usermod -aG docker $USER
EOF
)

echo 🐳 Проверяем наличие Docker Compose...
ssh %SSH_USER%@%SERVER_IP% "command -v docker-compose"
if errorlevel 1 (
    echo 📦 Устанавливаем Docker Compose...
    ssh %SSH_USER%@%SERVER_IP% << "EOF"
        sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
EOF
)

echo ⚙️ Настраиваем переменные окружения...
ssh %SSH_USER%@%SERVER_IP% << "EOF"
    cd %APP_DIR%
    if [ ! -f .env ]; then
        echo "BOT_TOKEN=your_bot_token_here" > .env
        echo ⚠️ Создан файл .env. Не забудьте добавить настоящий BOT_TOKEN!
    fi
EOF

echo 🚀 Запускаем Napominalkin Bot...
ssh %SSH_USER%@%SERVER_IP% "cd %APP_DIR% && docker-compose up -d --build"

echo 🔍 Проверяем статус контейнера...
ssh %SSH_USER%@%SERVER_IP% "cd %APP_DIR% && docker-compose ps"

echo.
echo ✅ Развертывание завершено!
echo.
echo 📝 Не забудьте:
echo 1. Добавить BOT_TOKEN в файл .env на сервере
echo 2. Перезапустить контейнер: docker-compose restart
echo 3. Проверить логи: docker-compose logs -f
echo.
echo 🎉 Ваш бот запущен на сервере %SERVER_IP%
echo.
pause
