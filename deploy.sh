#!/bin/bash

# Napominalkin Bot Deployment Script
# Автоматическая установка на удаленный сервер

set -e

# Цвета для вывода
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🚀 Начинаем развертывание Napominalkin Bot...${NC}"

# Проверяем наличие необходимых переменных
if [ -z "$1" ]; then
    echo -e "${RED}❌ Укажите IP адрес сервера: ./deploy.sh server_ip${NC}"
    exit 1
fi

SERVER_IP=$1
SSH_USER="${2:-napominalkin}"
APP_DIR="/home/$SSH_USER/napominalkin-bot"

echo -e "${YELLOW}📋 Целевой сервер: $SERVER_IP${NC}"
echo -e "${YELLOW}👤 Пользователь: $SSH_USER${NC}"
echo -e "${YELLOW}📁 Директория: $APP_DIR${NC}"

# Проверяем подключение к серверу
echo -e "${YELLOW}🔗 Проверяем подключение к серверу...${NC}"
if ! ssh "$SSH_USER@$SERVER_IP" "echo 'Подключение успешно!'"; then
    echo -e "${RED}❌ Не удалось подключиться к серверу${NC}"
    exit 1
fi

# Создаем директорию на сервере
echo -e "${YELLOW}📁 Создаем рабочую директорию...${NC}"
ssh "$SSH_USER@$SERVER_IP" "mkdir -p $APP_DIR"

# Копируем файлы на сервер
echo -e "${YELLOW}📤 Копируем файлы на сервер...${NC}"
scp -r ./* "$SSH_USER@$SERVER_IP:$APP_DIR/"

# Устанавливаем Docker на сервере (если не установлен)
echo -e "${YELLOW}🐳 Проверяем наличие Docker...${NC}"
if ! ssh "$SSH_USER@$SERVER_IP" "command -v docker &> /dev/null"; then
    echo -e "${YELLOW}📦 Устанавливаем Docker...${NC}"
    ssh "$SSH_USER@$SERVER_IP" << 'EOF'
        sudo apt update
        sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
        curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -
        sudo add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
        sudo apt update
        sudo apt install -y docker-ce docker-ce-cli containerd.io
        sudo usermod -aG docker $USER
EOF
fi

# Устанавливаем Docker Compose (если не установлен)
echo -e "${YELLOW}🐳 Проверяем наличие Docker Compose...${NC}"
if ! ssh "$SSH_USER@$SERVER_IP" "command -v docker-compose &> /dev/null"; then
    echo -e "${YELLOW}📦 Устанавливаем Docker Compose...${NC}"
    ssh "$SSH_USER@$SERVER_IP" << 'EOF'
        sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
        sudo chmod +x /usr/local/bin/docker-compose
EOF
fi

# Создаем .env файл если его нет
echo -e "${YELLOW}⚙️  Настраиваем переменные окружения...${NC}"
ssh "$SSH_USER@$SERVER_IP" << EOF
    cd $APP_DIR
    if [ ! -f .env ]; then
        echo "BOT_TOKEN=your_bot_token_here" > .env
        echo -e "${YELLOW}⚠️  Создан файл .env. Не забудьте добавить настоящий BOT_TOKEN!${NC}"
    fi
EOF

# Запускаем приложение
echo -e "${YELLOW}🚀 Запускаем Napominalkin Bot...${NC}"
ssh "$SSH_USER@$SERVER_IP" << 'EOF'
    cd $APP_DIR
    docker-compose up -d --build
EOF

# Проверяем статус
echo -e "${YELLOW}🔍 Проверяем статус контейнера...${NC}"
ssh "$SSH_USER@$SERVER_IP" "cd $APP_DIR && docker-compose ps"

echo -e "${GREEN}✅ Развертывание завершено!${NC}"
echo -e "${YELLOW}📝 Не забудьте:${NC}"
echo -e "1. Добавить BOT_TOKEN в файл .env на сервере"
echo -e "2. Перезапустить контейнер: docker-compose restart"
echo -e "3. Проверить логи: docker-compose logs -f"

echo -e "${GREEN}🎉 Ваш бот запущен на сервере $SERVER_IP${NC}"
