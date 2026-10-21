# Task Tracker API

Серверное приложение для управления задачами сотрудников. Проект реализует REST API с использованием Django REST Framework, предоставляя CRUD-операции для сотрудников и задач, а также специализированные аналитические эндпоинты для оценки загруженности.

## 🛠️ Стек технологий

*   **Язык**: Python 3.12+ (тестировалось на 3.14)
*   **Фреймворк**: Django 5.2.8+, Django REST Framework 3.16+
*   **База данных**: PostgreSQL 16
*   **Асинхронные задачи**: Celery 5.6+, Redis 7
*   **Документация**: drf-spectacular (Swagger/OpenAPI)
*   **Управление зависимостями**: Poetry
*   **Контейнеризация**: Docker, Docker Compose

## 📂 Структура проекта

```text
task_tracker/
├── config/                 # Настройки Django проекта (settings.py, urls.py)
├── tracker/                # Основное приложение
│   ├── migrations/         # Миграции базы данных
│   ├── models.py           # Модели Employee и Task
│   ├── serializers.py      # Сериализаторы DRF
│   ├── views.py            # ViewSets и аналитические эндпоинты
│   └── tests.py            # Тесты
├── .env.example            # Пример переменных окружения
├── docker-compose.yml      # Конфигурация Docker Compose
├── Dockerfile              # Инструкция сборки образа
├── manage.py               # Утилита управления Django
├── pyproject.toml          # Зависимости проекта (Poetry)
└── README.md               # Документация
```

## 🚀 Установка и запуск (Локально)

### 1. Требования
Убедитесь, что у вас установлены:
*   Python 3.12+
*   Poetry
*   PostgreSQL (запущенный локально или в Docker)

### 2. Клонирование и установка зависимостей
```bash
git clone https://github.com/NataKirp/task_tracker.git
cd task_tracker
poetry install
```

### 3. Настройка переменных окружения
Создайте файл `.env` в корне проекта на основе `.env.example`:
```env
SECRET_KEY=django-insecure-your-secret-key
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Настройки БД (если запускаете локально)
DB_NAME=task_tracker_db
DB_USER=postgres
DB_PASSWORD=postgres
DB_HOST=localhost
DB_PORT=5432

# Redis для Celery
CELERY_BROKER_URL=redis://localhost:6379/0
```

### 4. Миграции и запуск
```bash
# Применение миграций
poetry run python manage.py migrate

# Создание суперпользователя (опционально, для доступа к админке)
poetry run python manage.py createsuperuser

# Запуск сервера разработки
poetry run python manage.py runserver
```
Сервер будет доступен по адресу: `http://127.0.0.1:8000/`

## 🐳 Запуск через Docker Compose

Для быстрого развертывания всего стека (Django + PostgreSQL + Redis + Celery) используйте Docker:

1. Убедитесь, что файл `.env` настроен (в частности, `DB_HOST=db`).
2. Выполните сборку и запуск:
```bash
docker compose up -d --build
```
3. Примените миграции внутри контейнера:
```bash
docker compose exec web python manage.py migrate
```
Приложение будет доступно по адресу: `http://localhost:8000/`

## 📚 API Документация

Интерактивная документация API (Swagger UI) доступна после запуска сервера:
*   **Swagger UI**: `http://127.0.0.1:8000/api/docs/`
*   **OpenAPI Schema**: `http://127.0.0.1:8000/api/schema/`

### Основные эндпоинты

#### 1. Сотрудники (CRUD)
*   `GET /api/employees/` — Список сотрудников
*   `POST /api/employees/` — Создать сотрудника
*   `GET /api/employees/{id}/` — Детали сотрудника
*   `PUT/PATCH /api/employees/{id}/` — Обновить сотрудника
*   `DELETE /api/employees/{id}/` — Удалить сотрудника

#### 2. Задачи (CRUD)
*   `GET /api/tasks/` — Список задач
*   `POST /api/tasks/` — Создать задачу
*   `GET /api/tasks/{id}/` — Детали задачи
*   `PUT/PATCH /api/tasks/{id}/` — Обновить задачу
*   `DELETE /api/tasks/{id}/` — Удалить задачу

#### 3. Специальные эндпоинты (Аналитика)
*   `GET /api/analytics/busy_employees/` — Список сотрудников, отсортированный по количеству активных задач (по убыванию).
*   `GET /api/analytics/important_tasks/` — Список важных задач (не взятых в работу, но от которых зависят задачи в работе) с указанием рекомендуемого исполнителя.

## 🧪 Тестирование

Для запуска тестов используйте стандартную команду Django:
```bash
poetry run python manage.py test
```

Для проверки покрытия тестами:
```bash
poetry run coverage run manage.py test
poetry run coverage report
```

## 🎨 Форматирование кода

Проект использует `black`, `isort` и `flake8` для соблюдения стандартов PEP8.
```bash
poetry run black .
poetry run isort .
poetry run flake8 .
```

## 🌿 Gitflow

В проекте используется Gitflow. Ветки:
*   `main` — стабильный релиз
*   `develop` — основная ветка разработки
*   `feature/*` — новые фичи
*   `hotfix/*` — срочные исправления
```
