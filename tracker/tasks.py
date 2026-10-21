import logging
import os
from datetime import date, timedelta

import requests
from celery import shared_task
from django.contrib.auth import get_user_model

from .models import Task

User = get_user_model()

logger = logging.getLogger(__name__)

User = get_user_model()


def send_telegram_message(chat_id, text):
    """
    Вспомогательная функция для отправки сообщения.
    При ошибке выводит предупреждение в терминал через logging.
    """
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token or not chat_id:
        return False

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "HTML"}

    # proxies = {
    #     "http": "socks5h://127.0.0.1:1080",
    #     "https": "socks5h://127.0.0.1:1080"
    # }
    proxies = None

    try:
        response = requests.post(url, json=payload, proxies=proxies, timeout=10)
        response.raise_for_status()
        return True
    except requests.exceptions.ConnectionError:
        logger.error(
            "Не удалось отправить сообщение в Telegram для chat_id=%s. "
            "Причина: нет связи с api.telegram.org (Network unreachable).",
            chat_id,
        )
        return False
    except requests.exceptions.Timeout:
        logger.warning("Таймаут при отправке в Telegram для chat_id=%s.", chat_id)
        return False
    except requests.exceptions.RequestException as e:
        logger.error("Ошибка при отправке в Telegram: %s", e)
        return False


@shared_task
def check_deadlines():
    """
    Фоновая задача: ищет задачи, у которых дедлайн завтра,
    и которые еще не выполнены. Отправляет напоминание исполнителю.
    """
    tomorrow = date.today() + timedelta(days=1)

    # Ищем задачи: срок - завтра, статус не 'done', и у задачи есть исполнитель с telegram_id
    tasks = Task.objects.filter(
        due_date=tomorrow,
        status__in=["new", "in_progress"],
        assignee__telegram_id__isnull=False,
    ).exclude(assignee__telegram_id="")

    for task in tasks:
        user = task.assignee
        message = (
            f"🔔 <b>Напоминание о дедлайне!</b>\n\n"
            f"Задача: <b>{task.name}</b>\n"
            f"Срок сдачи: <u>завтра ({task.due_date})</u>\n"
            f"Текущий статус: {task.get_status_display()}\n\n"
            f"Пожалуйста, не забудьте выполнить её вовремя!"
        )

        send_telegram_message(user.telegram_id, message)

    return f"Проверено задач: {tasks.count()}"
