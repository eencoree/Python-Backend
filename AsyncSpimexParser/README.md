Async Spimex ETL Parser

Асинхронный ETL-пайплайн для сбора данных торгов SPIMEX (нефтепродукты), их обработки и загрузки в базу данных.

---

## Возможности

- Асинхронный обход страниц сайта SPIMEX
- Сбор ссылок на PDF/XLS файлы
- Скачивание файлов через aiohttp
- Извлечение и обработка данных (extract / transform / load)
- Очистка и нормализация данных через pandas
- Загрузка в SQLAlchemy (async ORM)
- Поддержка concurrency
- Retry-механизм обработки файлов
- Логирование всех этапов ETL
- Тестирование (unit / integration / mock)

---

## Архитектура

ETL состоит из четырёх основных этапов:

### 1. Links (Extract URLs)
- Парсинг HTML страниц
- Извлечение ссылок на файлы
- Фильтрация по дате и типу файла

### 2. Extract
- Скачивание PDF/XLS
- Преобразование в DataFrame

### 3. Transform
- Очистка данных (`clean_df`)
- Приведение типов
- Формирование финальной структуры (`transform_df`)

### 4. Load
- Асинхронная загрузка в БД
- Bulk insert через SQLAlchemy

---

## Запуск проекта
### Запуск ETL

```bash
python cli.py run --start-date 2026-04-23 --end-date 2026-04-24
```
### Запуск тестов
```bash
pytest -v
```

### Docker запуск
#### Сборка
```bash
docker build -t spimex-etl .
```
#### Запуск контейнера
```bash
docker run --rm spimex-etl
```

### Docker Compose запуск
#### Запуск со сборкой
```bash
docker-compose up --build
```
#### Остановка
```bash
docker-compose down
```