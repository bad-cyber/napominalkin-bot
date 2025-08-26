# 🔒 Руководство по безопасному развертыванию Napominalkin Bot

## 🎯 Варианты безопасного развертывания

### Вариант 1: Использование Telegram Web App Hosting (Рекомендуется)
Telegram предоставляет безопасный хостинг для Web App файлов:

1. **Загрузите файлы на GitHub Pages или GitLab Pages** (бесплатно)
2. **Используйте Netlify или Vercel** (бесплатные варианты)
3. **Обновите URL в коде бота**:

```python
WebAppInfo(url="https://your-username.github.io/napominalkin-bot/code.html")
```

### Вариант 2: Защищенный удаленный сервер

#### Настройка сервера:
```bash
# Установите базовые пакеты безопасности
sudo apt update && sudo apt upgrade -y
sudo apt install fail2ban ufw -y

# Настройте фаервол
sudo ufw allow ssh
sudo ufw allow http
sudo ufw allow https
sudo ufw enable

# Создайте отдельного пользователя для бота
sudo adduser napominalkin
sudo usermod -aG sudo napominalkin
```

#### Настройка бота:
```bash
# Скопируйте файлы на сервер
scp -r napominalkin-bot/ napominalkin@your-server-ip:/home/napominalkin/

# Установите зависимости
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Вариант 3: Использование Docker (Самый безопасный)

Создайте `Dockerfile`:

```dockerfile
FROM python:3.9-slim

WORKDIR /app

# Создаем непривилегированного пользователя
RUN useradd -m -u 1000 napominalkin && \
    chown -R napominalkin:napominalkin /app

# Копируем файлы
COPY --chown=napominalkin:napominalkin . .

USER napominalkin

# Устанавливаем зависимости
RUN pip install --no-cache-dir -r requirements.txt

# Запускаем бота
CMD ["python", "main.py"]
```

И `docker-compose.yml`:

```yaml
version: '3.8'

services:
  napominalkin-bot:
    build: .
    restart: unless-stopped
    volumes:
      - ./data:/app/data
    environment:
      - BOT_TOKEN=${BOT_TOKEN}
    networks:
      - napominalkin-net

networks:
  napominalkin-net:
    driver: bridge
```

## 🔐 Безопасность данных

### 1. Защита конфиденциальных данных
```bash
# .env файл (никогда не коммитьте в git!)
BOT_TOKEN=your_bot_token_here
# Добавьте в .gitignore
echo ".env" >> .gitignore
echo "*.json" >> .gitignore
```

### 2. Безопасная база данных
Замените JSON файлы на настоящую БД:

```python
# Используйте PostgreSQL вместо JSON
import psycopg2
import os

DATABASE_URL = os.getenv('DATABASE_URL')

class Database:
    def __init__(self):
        self.conn = psycopg2.connect(DATABASE_URL)
        self.create_tables()
```

### 3. HTTPS для Web App
Обязательно используйте HTTPS для Web App:
- Бесплатные сертификаты: Let's Encrypt
- Автоматическое обновление: Certbot

## 🚀 Инструкции по развертыванию

### Для GitHub Pages:
1. Создайте репозиторий на GitHub
2. Загрузите только `code.html` файл
3. В настройках репозитория включите GitHub Pages
4. Получите URL вида: `https://username.github.io/repository-name/code.html`

### Для Docker развертывания:
```bash
# Соберите образ
docker build -t napominalkin-bot .

# Запустите контейнер
docker run -d \
  --name napominalkin-bot \
  -e BOT_TOKEN=your_token_here \
  -v $(pwd)/data:/app/data \
  napominalkin-bot
```

## 📊 Мониторинг и логи

### Настройка логирования:
```python
# Добавьте в main.py
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)
```

### Мониторинг работы:
```bash
# Просмотр логов
tail -f bot.log

# Проверка статуса бота
systemctl status napominalkin-bot
```

## 🛡️ Дополнительные меры безопасности

1. **Регулярные обновления**: `sudo apt update && sudo apt upgrade`
2. **Резервное копирование**: Настройте автоматическое backup данных
3. **Мониторинг**: Используйте monitoring tools like Prometheus + Grafana
4. **Rate limiting**: Добавьте ограничение запросов к боту

## 📞 Поддержка

Если возникнут проблемы с развертыванием:
1. Проверьте логи: `journalctl -u napominalkin-bot`
2. Убедитесь, что токен бота корректен
3. Проверьте доступ к интернету с сервера

**Ваш бот готов к безопасной работе!** 🎉
