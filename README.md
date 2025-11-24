# SmartMirror Backend - Python

Python backend для проекта SmartMirror

```
smart-mirror-backend/
│
├── app/                          # Основное приложение
│   ├── __init__.py
│   ├── main.py                   # Точка входа FastAPI приложения
│   │
│   ├── api/                      # API Gateway
│   │   ├── __init__.py
│   │   ├── endpoints/            # Эндпоинты REST API
│   │   │   ├── __init__.py
│   │   │   ├── users.py          # Управление пользователями
│   │   │   ├── llm.py            # Запросы к LLM
│   │   │   ├── weather.py        # API погоды
│   │   │   ├── music.py          # Стриминг Яндекс.Музыки
│   │   │   ├── firmware.py       # Подтягивание прошивки
│   │   │   ├── config.py         # Настройки (WiFi, токены)
│   │   │   └── stats.py          # Логирование и статистика
│   │   │
│   │   └── middleware/           # Middleware (аутентификация, логи)
│   │       ├── __init__.py
│   │       ├── auth.py
│   │       └── logging.py
│   │
│   ├── core/                     # Ядро приложения
│   │   ├── __init__.py
│   │   ├── config.py             # Конфигурация приложения
│   │   ├── security.py           # Безопасность, JWT, хеширование
│   │   └── dependencies.py       # Dependency injection
│   │
│   ├── models/                   # Database модели (ORM)
│   │   ├── __init__.py
│   │   ├── user.py               # Модель пользователя
│   │   ├── context.py            # Контексты пользователей для LLM
│   │   ├── api_key.py            # Ключи для аккаунтов
│   │   └── stats.py              # Статистика использования
│   │
│   ├── schemas/                  # Pydantic схемы (валидация данных)
│   │   ├── __init__.py
│   │   ├── user.py               # Схемы пользователя
│   │   ├── llm.py                # Схемы запросов/ответов LLM
│   │   ├── weather.py            # Схемы погоды
│   │   └── music.py              # Схемы музыки
│   │
│   ├── services/                 # Бизнес-логика
│   │   ├── __init__.py
│   │   │
│   │   ├── llm/                  # Локальная LLM
│   │   │   ├── __init__.py
│   │   │   ├── model.py          # Загрузка и работа с моделью
│   │   │   └── processor.py      # Обработка запросов
│   │   │
│   │   ├── users/                # Управление пользователями
│   │   │   ├── __init__.py
│   │   │   ├── manager.py        # CRUD пользователей
│   │   │   └── context.py        # Управление контекстами
│   │   │
│   │   ├── weather/              # Погода
│   │   │   ├── __init__.py
│   │   │   └── service.py        # Интеграция с Weather API
│   │   │
│   │   └── music/                # Музыка
│   │       ├── __init__.py
│   │       └── yandex.py         # Стриминг Яндекс.Музыки
│   │
│   ├── database/                 # База данных
│   │   ├── __init__.py
│   │   ├── session.py            # Сессии БД
│   │   └── base.py               # Base модели
│   │
│   ├── utils/                    # Утилиты
│   │   ├── __init__.py
│   │   ├── logger.py             # Настройка логирования
│   │   └── helpers.py            # Вспомогательные функции
│   │
│   └── web/                      # Web интерфейс
│       ├── __init__.py
│       ├── templates/            # HTML шаблоны
│       │   ├── setup.html        # Настройка WiFi
│       │   └── tokens.html       # Ввод токенов музыки
│       └── static/               # Статические файлы (CSS, JS)
│
├── logs/                         # Логи приложения
│   └── .gitkeep
│
├── tests/                        # Тесты
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_api/
│   ├── test_services/
│   └── test_models/
│
├── .gitignore
├── env.example                   # Пример файла окружения
├── Makefile                      # Команды для разработки
├── pyproject.toml                # Конфигурация проекта и зависимости
├── requirements.txt              # Зависимости (опционально)
└── README.md
```

