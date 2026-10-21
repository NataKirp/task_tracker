from django.test import TestCase
from django.utils import timezone
from datetime import timedelta
from users.models import User
from .models import Task
from .serializers import TaskSerializer


class TaskModelTests(TestCase):
    """
    Тесты для модели Task и её бизнес-логики.
    """

    def setUp(self):
        self.user = User.objects.create_user(username="tester", password="pass")
        self.parent_task = Task.objects.create(
            name="Родительская задача",
            due_date=timezone.now().date() + timedelta(days=7),
            status="new"
        )

    def test_task_str(self):
        """Проверяем строковое представление задачи."""
        self.assertEqual(str(self.parent_task), "Родительская задача")

    def test_parent_task_does_not_close_if_subtasks_are_open(self):
        """
        Родительская задача НЕ должна закрываться, если есть незавершенные подзадачи.
        """
        subtask2 = Task.objects.create(
            name="Подзадача 2",
            parent_task=self.parent_task,
            due_date=timezone.now().date() + timedelta(days=2),
            status="in_progress"
        )
        subtask1 = Task.objects.create(
            name="Подзадача 1",
            parent_task=self.parent_task,
            due_date=timezone.now().date() + timedelta(days=1),
            status="done"
        )

        # Обновляем статус родителя (чтобы сработал save(), но он не должен закрыться)
        self.parent_task.refresh_from_db()
        # Проверяем: родитель ДОЛЖЕН остаться 'new', так как subtask2 еще в работе
        self.assertEqual(self.parent_task.status, "new")

    def test_parent_task_closes_when_all_subtasks_are_done(self):
        """
        Родительская задача ДОЛЖНА автоматически закрыться,
        когда все её подзадачи переведены в статус 'done'.
        """
        subtask1 = Task.objects.create(
            name="Подзадача 1",
            parent_task=self.parent_task,
            due_date=timezone.now().date() + timedelta(days=1),
            status="in_progress"
        )
        subtask2 = Task.objects.create(
            name="Подзадача 2",
            parent_task=self.parent_task,
            due_date=timezone.now().date() + timedelta(days=2),
            status="in_progress"
        )

        subtask1.status = "done"
        subtask1.save()
        self.parent_task.refresh_from_db()
        self.assertEqual(self.parent_task.status, "new")

        subtask2.status = "done"
        subtask2.save()

        # Обновляем данные родителя из БД и проверяем статус
        self.parent_task.refresh_from_db()
        # ТЕПЕРЬ он должен быть 'done' благодаря переопределению save()
        self.assertEqual(self.parent_task.status, "done")


class TaskSerializerTests(TestCase):
    """
    Тесты для проверки валидации данных в TaskSerializer.
    """

    def test_due_date_in_past_raises_error(self):
        """Проверяем, что сериализатор не пропускает прошедшую дату."""
        past_date = timezone.now().date() - timedelta(days=1)

        # Создаем "сырые" данные, имитируя запрос от клиента
        data = {
            'name': 'Просроченная задача',
            'status': 'new',
            'due_date': past_date
        }

        serializer = TaskSerializer(data=data)

        # Метод is_valid() запускает валидацию.
        # Мы ожидаем, что он вернет False, так как дата в прошлом.
        self.assertFalse(serializer.is_valid())

        # Проверяем, что ошибка привязана именно к полю due_date
        self.assertIn('due_date', serializer.errors)