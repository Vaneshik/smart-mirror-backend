# SmartMirror Backend

Python backend для проекта SmartMirror с интеграцией LLM (DeepSeek) и Яндекс.Музыки

## 🚀 Быстрый старт

```bash
# Установка зависимостей
make dev

# Настройка окружения
cp env.example .env
# Заполните .env файл API ключами

# Запуск сервера
make run
```

**Production сервер:** http://94.228.117.244  
**Локально:** `http://localhost:8000`  
**Документация API:** http://94.228.117.244/docs

## 📋 API Endpoints

### 1. LLM - Запрос к языковой модели

**Endpoint:** `POST /api/llm/query`

**Описание:** Отправляет текстовый запрос к DeepSeek API и возвращает ответ

**Request Body:**
```json
{
  "text": "Привет, как дела?"
}
```

**Response:**
```json
{
  "response": "Здравствуйте! Хорошо, спасибо!"
}
```

**Пример (текстовый запрос):**
```bash
# Production
curl -X POST "http://94.228.117.244/api/llm/query" -H "Content-Type: application/json" -d '{"text": "Расскажи анекдот"}'

# Локально
curl -X POST "http://localhost:8000/api/llm/query" -H "Content-Type: application/json" -d '{"text": "Расскажи анекдот"}'
```

**Пример (музыкальная команда):**
```bash
curl -X POST "http://localhost:8000/api/llm/query" \
  -H "Content-Type: application/json" \
  -d '{"text": "Включи Моргенштерна"}'

# Сервер выполнит поиск и вернёт stream URL первого найденного трека:
# {
#   "stream_url": "https://storage.mds.yandex.net/get-mp3/..."
# }
```

---

### 2. Музыка - Поиск треков

**Endpoint:** `GET /api/music/search`

**Описание:** Поиск треков в Яндекс.Музыке

**Query Parameters:**
- `q` (required) - поисковый запрос

**Response:**
```json
{
  "tracks": [
    {
      "id": "123456",
      "title": "Enter Sandman",
      "artist": "Metallica",
      "album": "Metallica",
      "duration_ms": 331000,
      "cover_url": "https://avatars.yandex.net/..."
    }
  ],
  "total": 1
}
```

**Пример:**
```bash
# Production
curl -G "http://94.228.117.244/api/music/search" --data-urlencode "q=Моргенштерн"

# Локально
curl -G "http://localhost:8000/api/music/search" --data-urlencode "q=Моргенштерн"
```

---

### 3. Музыка - Получение stream URL

**Endpoint:** `GET /api/music/track/{track_id}/stream`

**Описание:** Возвращает прямую ссылку на трек для стриминга/скачивания

**Path Parameters:**
- `track_id` - ID трека из результатов поиска

**Response:**
```json
{
  "stream_url": "https://storage.mds.yandex.net/get-mp3/..."
}
```

**Пример:**
```bash
# Production
curl "http://94.228.117.244/api/music/track/123456/stream"

# Локально
curl "http://localhost:8000/api/music/track/123456/stream"
```

**Воспроизведение:**
```bash
# Получить URL и воспроизвести (production)
STREAM_URL=$(curl "http://94.228.117.244/api/music/track/123456/stream" | jq -r '.stream_url')
mpv "$STREAM_URL"
```

---

### 4. Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "ok"
}
```

**Пример:**
```bash
# Production
curl http://94.228.117.244/health

# Локально
curl http://localhost:8000/health
```

## ⚙️ Конфигурация

Создайте файл `.env` из `env.example`:

```bash
cp env.example .env
```

Заполните необходимые ключи:

```env
# DeepSeek LLM API - Primary (artemox)
DEEPSEEK_API_KEY=your-artemox-api-key
DEEPSEEK_BASE_URL=https://api.artemox.com/v1

# DeepSeek LLM API - Fallback (deepseek official)
DEEPSEEK_FALLBACK_API_KEY=your-deepseek-api-key
DEEPSEEK_FALLBACK_BASE_URL=https://api.deepseek.com/v1

# Yandex Music (получить OAuth токен)
YANDEX_MUSIC_TOKEN=y0_xxxxxxxxxxxxx
```

**Fallback механизм:**
- Сначала пытается Primary (artemox) с 2 попытками
- Если не работает - автоматически переключается на Fallback (deepseek) с 2 попытками
- Timeout 10 секунд для быстрого отклика умной колонки

## 🛠 Команды разработки

```bash
make install    # Установить зависимости
make dev        # Установить зависимости для разработки
make run        # Запустить сервер
make test       # Запустить тесты
make format     # Форматировать код (black + ruff)
make lint       # Проверить код (ruff, mypy)
make clean      # Очистить временные файлы
```

## 📁 Структура проекта

```
smart-mirror-backend/
├── app/
│   ├── main.py                   # FastAPI приложение
│   ├── core/
│   │   └── config.py            # Настройки приложения
│   ├── api/endpoints/
│   │   ├── llm.py               # LLM endpoints
│   │   └── music.py             # Music endpoints
│   ├── services/
│   │   ├── llm/
│   │   │   └── deepseek.py      # DeepSeek API сервис
│   │   └── music/
│   │       └── yandex.py        # Яндекс.Музыка сервис
│   └── schemas/
│       ├── llm.py               # Pydantic схемы для LLM
│       └── music.py             # Pydantic схемы для музыки
├── tests/                        # Тесты
├── .env                         # Конфигурация (не в git)
├── env.example                  # Пример конфигурации
├── pyproject.toml               # Конфигурация проекта
├── Makefile                     # Команды для разработки
└── README.md                    # Документация
```

## 🎯 Интеграция с ROS

Пример использования в ROS-ноде:

```python
import httpx

# Используйте production API или localhost
API_URL = "http://94.228.117.244"  # или "http://localhost:8000"

# LLM запрос
async with httpx.AsyncClient() as client:
    response = await client.post(
        f"{API_URL}/api/llm/query",
        json={"text": "Привет!"}
    )
    llm_answer = response.json()["response"]

# Поиск музыки
async with httpx.AsyncClient() as client:
    response = await client.get(
        f"{API_URL}/api/music/search",
        params={"q": "Metallica"}
    )
    tracks = response.json()["tracks"]

# Получить stream URL и воспроизвести
track_id = tracks[0]["id"]
response = await client.get(
    f"{API_URL}/api/music/track/{track_id}/stream"
)
stream_url = response.json()["stream_url"]

# Воспроизвести с помощью subprocess + mpv
import subprocess
subprocess.Popen(['mpv', '--no-video', stream_url])
```

## 📦 Требования

- Python >= 3.9
- Зависимости указаны в `pyproject.toml`

## 🔗 Полезные ссылки

- **DeepSeek API**: https://platform.deepseek.com/
- **Яндекс OAuth**: https://oauth.yandex.ru/
- **FastAPI документация**: https://fastapi.tiangolo.com/
- **Swagger UI (Production)**: http://94.228.117.244/docs
- **Swagger UI (Local)**: http://localhost:8000/docs

## 🔗 GitHub

**Репозиторий**: https://github.com/Vaneshik/smart-mirror-backend

## 📝 Лицензия

MIT
