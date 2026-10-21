FROM python:3.12-slim

# Замена apt-зеркала на Яндекс
RUN sed -i 's|deb.debian.org|mirror.yandex.ru|g' /etc/apt/sources.list.d/debian.sources 2>/dev/null || \
    sed -i 's|deb.debian.org|mirror.yandex.ru|g' /etc/apt/sources.list 2>/dev/null || true

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Установка Poetry
RUN pip install "poetry==2.2.1" "poetry-plugin-pypi-mirror" -i https://pypi-mirror.gitverse.ru/simple/

# Настройка Poetry
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    POETRY_VIRTUALENVS_CREATE=false \
    POETRY_PYPI_MIRROR_URL=https://pypi-mirror.gitverse.ru/simple/ \
    POETRY_REQUESTS_TIMEOUT=300 \
    POETRY_MAX_WORKERS=1

# Копирование зависимостей и установка
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-interaction

# Копирование кода
COPY . .

# Запуск
CMD ["gunicorn", "config.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "3", "--timeout", "60"]
