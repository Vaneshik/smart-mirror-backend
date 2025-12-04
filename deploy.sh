#!/bin/bash
set -e

echo "🚀 Starting deployment..."

# Переменные
APP_DIR="/opt/smart-mirror-backend"
SERVICE_NAME="smartmirror"

# Обновление кода
echo "📦 Pulling latest code..."
cd $APP_DIR
git pull origin main

# Активация виртуального окружения
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Установка зависимостей
echo "📚 Installing dependencies..."
pip install -e .

# Перезапуск сервиса
echo "🔄 Restarting service..."
sudo systemctl restart $SERVICE_NAME

# Проверка статуса
echo "✅ Checking service status..."
sudo systemctl status $SERVICE_NAME --no-pager

echo "🎉 Deployment completed successfully!"

