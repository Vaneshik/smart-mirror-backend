.PHONY: help install dev run test clean format lint

help:
	@echo "SmartMirror Backend - Available commands:"
	@echo "  make install    - Установить зависимости"
	@echo "  make dev        - Установить зависимости для разработки"
	@echo "  make run        - Запустить сервер"
	@echo "  make test       - Запустить тесты"
	@echo "  make format     - Форматировать код (black + ruff)"
	@echo "  make lint       - Проверить код (ruff, mypy)"
	@echo "  make clean      - Очистить временные файлы"
	@echo "  make db-init    - Инициализировать БД"
	@echo "  make db-migrate - Создать миграцию"
	@echo "  make db-upgrade - Применить миграции"

install:
	pip3 install -e .

dev:
	pip3 install -e ".[dev]"

run:
	python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

test:
	pytest tests/ -v --cov=app --cov-report=html

format:
	black app/ tests/
	ruff check --fix app/ tests/

lint:
	ruff check app/ tests/
	mypy app/

clean:
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} +
	rm -rf .pytest_cache .mypy_cache .ruff_cache htmlcov

# db-init:
# 	python -m app.database.init_db

# db-migrate:
# 	alembic revision --autogenerate -m "$(message)"

# db-upgrade:
# 	alembic upgrade head

# db-downgrade:
# 	alembic downgrade -1

