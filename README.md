# Tech Store Backend

Серверная часть и REST API интернет-магазина техники. Вариант ТЗ: **Python + PostgreSQL**.

## Стек

| Назначение      | Технология                            |
|-----------------|---------------------------------------|
| Фреймворк       | FastAPI, Uvicorn                      |
| СУБД            | PostgreSQL 16                         |
| ORM             | SQLAlchemy                            |
| Кеширование     | Redis                                 |
| Аутентификация  | JWT (PyJWT), пароли хешируются Argon2 |
| Контейнеризация | Docker (multi-stage), Docker Compose  |
| Хостинг         | Koyeb (деплой из Dockerfile)          |
| Медиа           | Supabase Storage                      |

## Деплой и документация API

- Рабочий деплой: `https://tech-store-app-backend.onrender.com/docs#`

Локально Swagger доступен по адресу http://localhost:8000/docs.

## Локальный запуск через Docker Compose

1. Склонировать репозиторий и перейти в его папку:

   ```bash
   git clone https://github.com/sKITggge/tech-store-app-backend
   cd tech-store-app-backend
   ```

2. Создать файл окружения из шаблона:

   ```bash
   cp .env.example .env
   ```

3. Заполнить `.env`. Для запуска в Compose важно:
    - `POSTGRES_DB`, `POSTGRES_USER`, `POSTGRES_PASSWORD` задайте свои значения;
    - `REDIS_URL=redis://redis:6379`;
    - `JWT_SECRET_KEY` сгенерируйте: `openssl rand -hex 32`;
    - `ADMIN_EMAIL` и `ADMIN_PASSWORD` задайте для администратора.

   `DATABASE_URL` для контейнера `app` собирается автоматически из `POSTGRES_*` (хост `db`), значение из `.env`.

4. Собрать и запустить сервисы:

   ```bash
   docker compose up --build
   ```

   Поднимаются три сервиса: `app` (API, порт `8000`), `db` (PostgreSQL, порт `5432`), `redis` (порт `6379`). `app`
   стартует после того, как `db` и `redis` прошли healthcheck. Таблицы и первый админ создаются при старте приложения.

5. Проверить работу:
    - http://localhost:8000/ — ответ `{"message": "Hello"}`;
    - http://localhost:8000/docs — Swagger UI;
    - `GET http://localhost:8000/api/products` — каталог.

6. Остановить:

   ```bash
   docker compose down
   ```

Данные PostgreSQL хранятся в именованном томе `pgdata` и переживают перезапуски.

## Запуск без Docker (для разработки)

Нужны Python 3.12, запущенные PostgreSQL и Redis.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

## Структура проекта

```
app/
├── main.py            # приложение FastAPI, CORS, lifespan (init_db, seed админа)
├── api/routers/       # auth, catalog, cart
├── auth/              # зависимости: текущий пользователь, проверка роли admin
├── core/              # настройки, enum-ы, безопасность (Argon2, JWT)
├── db/                # сессия, init_db, seed, Redis-кеш
├── models/            # SQLAlchemy-модели: User, Product, Image, Cart, CartItem
├── schemas/           # Pydantic-схемы
└── utils/             # промокод, экранирование поиска
```