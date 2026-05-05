# SpimexFastAPI

FastAPI-сервис для обработки и анализа торговых данных с поддержкой кеширования, асинхронной работы с БД и системой
миграций.

---

## Возможности

- Получение торговых данных (results, dynamics, dates)
- Асинхронная работа через `AsyncSQLAlchemy`
- Кеширование через Redis
- Переменные окружения .env.example
- Миграции базы данных через Alembic
- Unit и integration тесты (pytest + httpx)
- Dependency Injection через FastAPI `Depends`
- Middleware для логирования запросов
- Healthcheck endpoint

---

## Сборка через Docker

```bash
docker-compose up --build
```

---

## Применение миграций

```bash
python -m alembic upgrade head
```

---

## Запуск приложения

```bash
uvicorn app.main:app --reload
```

---

## Swagger

```text
http://localhost:8000/docs
```

---

## API Endpoints

### Trading dates

```http request
GET /api/v1/trading/dates
```

### Trading results

```http request
GET /api/v1/trading/results?limit=100
```

### Trading dynamics

```http request
GET /api/v1/trading/dynamics?start_date=2024-01-01&end_date=2024-01-10
```

### Healthcheck

```http request
GET /api/health
```

---

## Тестирование

### Unit tests

```bash
pytest tests/unit
```

### Integration tests

```bash
pytest tests/integration
```

### All tests

```bash
pytest -v
```