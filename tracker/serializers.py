from django.contrib.auth import get_user_model
from django.utils import timezone
from rest_framework import serializers
from .models import Task
from users.serializers import UserSerializer

User = get_user_model()

class TaskSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Task (Задача).

    Особенности реализации:
    1. Использует вложенные сериализаторы (UserSerializer) для полей связей (assignee, parent_task).
       Это позволяет при GET-запросах возвращать полную информацию об объектах, а не только их ID.
    2. Для создания и обновления (POST/PUT/PATCH) использует поля с суффиксом `_id`.
       Это необходимо, чтобы клиент передавал только ID связанных сущностей,
       а не пытался создать их заново.
    """
    # Поля только для чтения (GET) - отдают вложенные объекты
    assignee = UserSerializer(read_only=True)
    parent_task = serializers.StringRelatedField(read_only=True)

    # Поля только для записи (POST/PUT/PATCH) - принимают ID связанных объектов
    assignee_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        source='assignee',
        write_only=True,
        required=False,
        allow_null=True
    )
    parent_task_id = serializers.PrimaryKeyRelatedField(
        queryset=Task.objects.all(),
        source='parent_task',
        write_only=True,
        required=False,
        allow_null=True
    )

    class Meta:
        model = Task
        fields = [
            'id', 'name', 'status', 'due_date',
            'assignee', 'assignee_id',
            'parent_task', 'parent_task_id'
        ]

    def validate_due_date(self, value):
        """
        Валидатор для поля `due_date` (Срок выполнения).

        Бизнес-правило:
            Запрещает создание или обновление задачи с датой в прошлом.

        Args:
            value (date): Дата, переданная клиентом в запросе.

        Raises:
            serializers.ValidationError: Если дата меньше текущей даты.

        Returns:
            date: Валидная дата (если проверка пройдена).
        """
        if value < timezone.now().date():
            raise serializers.ValidationError("Срок не может быть в прошлом.")
        return value
