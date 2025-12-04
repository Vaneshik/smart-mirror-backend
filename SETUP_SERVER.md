# Настройка сервера для CI/CD

## 1. Подготовка сервера (один раз)

### Подключитесь к серверу:
```bash
ssh root@94.228.117.244
```

### Установите необходимые пакеты:
```bash
# Обновите систему
sudo apt update && sudo apt upgrade -y

# Установите Python 3.9+, pip, venv, git
sudo apt install -y python3 python3-pip python3-venv git

# Установите дополнительные зависимости
sudo apt install -y build-essential libssl-dev libffi-dev
```

### Создайте директорию для приложения:
```bash
mkdir -p /opt/smart-mirror-backend
```

### Клонируйте репозиторий:
```bash
cd /opt/smart-mirror-backend
git clone https://github.com/Vaneshik/smart-mirror-backend.git .
```

### Создайте виртуальное окружение:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -e .
```

### Создайте .env файл:
```bash
nano .env
```

Вставьте:
```env
HOST=0.0.0.0
PORT=8000
DEBUG=False
SECRET_KEY=your-secret-key-here
DEEPSEEK_API_KEY=your-token
DEEPSEEK_BASE_URL=https://api.artemox.com/v1
DEEPSEEK_MODEL=deepseek-chat
DEEPSEEK_TIMEOUT=30
YANDEX_MUSIC_TOKEN=your-token
```

### Установите systemd service:
```bash
# Скопируйте service файл
cp smartmirror.service /etc/systemd/system/

# Перезагрузите systemd
systemctl daemon-reload

# Запустите сервис
systemctl enable smartmirror
systemctl start smartmirror

# Проверьте статус
systemctl status smartmirror
```

### (Для root это не требуется - пропускаем этот шаг)

### Сделайте deploy.sh исполняемым:
```bash
chmod +x /opt/smart-mirror-backend/deploy.sh
```

---

## 2. Настройка GitHub Actions (один раз)

### Сгенерируйте SSH ключ на вашем компьютере:
```bash
ssh-keygen -t ed25519 -C "github-actions" -f ~/.ssh/smartmirror_deploy
```

### Скопируйте публичный ключ на сервер:
```bash
ssh-copy-id -i ~/.ssh/smartmirror_deploy.pub your-user@94.228.117.244
```

### Добавьте секреты в GitHub:

1. Зайдите в репозиторий на GitHub
2. Settings → Secrets and variables → Actions
3. Добавьте два секрета:

**SSH_USER**
```
root
```

**SSH_PRIVATE_KEY**
```
(вставьте содержимое файла ~/.ssh/smartmirror_deploy)
```

Чтобы посмотреть приватный ключ:
```bash
cat ~/.ssh/smartmirror_deploy
```

---

## 3. Проверка работы

### Тест деплоя вручную:
```bash
ssh root@94.228.117.244 "cd /opt/smart-mirror-backend && ./deploy.sh"
```

### Тест автоматического деплоя:
```bash
# Сделайте любое изменение и запушьте
git add .
git commit -m "test: CI/CD"
git push origin main

# Откройте GitHub Actions в браузере и следите за прогрессом:
# https://github.com/Vaneshik/smart-mirror-backend/actions
```

### Проверка работы API:
```bash
# Проверьте что сервер отвечает
curl http://94.228.117.244:8000/health

# LLM тест
curl -X POST "http://94.228.117.244:8000/api/llm/query" \
  -H "Content-Type: application/json" \
  -d '{"text": "Привет!"}'

# Music тест
curl -G "http://94.228.117.244:8000/api/music/search" \
  --data-urlencode "q=Metallica"
```

---

## 4. Логи и мониторинг

### Просмотр логов сервиса:
```bash
# Следить за логами в реальном времени
journalctl -u smartmirror -f

# Последние 100 строк
journalctl -u smartmirror -n 100

# За последний час
journalctl -u smartmirror --since "1 hour ago"
```

### Управление сервисом:
```bash
# Перезапуск
systemctl restart smartmirror

# Остановка
systemctl stop smartmirror

# Запуск
systemctl start smartmirror

# Статус
systemctl status smartmirror
```

---

## 5. Firewall (если нужно)

```bash
# Откройте порт 8000
ufw allow 8000/tcp

# Проверьте статус
ufw status
```

---

## Готово! 🎉

Теперь при каждом push в main ветку:
1. GitHub Actions автоматически подключится к серверу
2. Обновит код
3. Установит зависимости
4. Перезапустит сервис

Backend будет доступен по адресу: http://94.228.117.244:8000

