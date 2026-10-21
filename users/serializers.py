from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Position

User = get_user_model()


class PositionSerializer(serializers.ModelSerializer):
    """
    Сериализатор для модели Position (Справочник должностей).

    Используется для:
    1. Отображения списка доступных должностей в API.
    2. Вложенного отображения должности внутри объекта Сотрудника (UserSerializer).

    Поля:
        id (int): Уникальный идентификатор должности.
        name (str): Название должности (например, "Разработчик").
    """

    class Meta:
        model = Position
        fields = ['id', 'name']


class UserSerializer(serializers.ModelSerializer):
    """
    Сериализатор для кастомной модели User (Сотрудника).

    Особенности реализации:
    1. Поле `position` используется только для чтения (read_only).
       При GET-запросе оно возвращает вложенный объект должности целиком
       (например, {"id": 1, "name": "Разработчик"}), а не просто её ID.
    2. Поле `position_id` используется только для записи (write_only).
       При создании (POST) или обновлении (PATCH) сотрудника клиент
       передает только идентификатор должности.
    3. Поле `password` имеет флаг write_only=True. Это гарантирует,
       что пароль никогда не попадет в ответ API.
    """

    # Вложенный сериализатор для чтения полной информации о должности
    position = PositionSerializer(read_only=True)

    # Поле для записи ID должности при создании/обновлении сотрудника
    position_id = serializers.PrimaryKeyRelatedField(
        queryset=Position.objects.all(),
        source='position',  # Указываем, что это поле пишет напрямую в поле position модели
        write_only=True,
        required=False
    )

    class Meta:
        model = User
        fields = [
            'id', 'username', 'password', 'first_name', 'last_name',
            'email', 'position', 'position_id', 'is_staff'
        ]

        # Скрываем пароль из всех ответов API (безопасность)
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        """
        Создание нового сотрудника с безопасным хранением пароля.

        Переопределяет стандартный метод create для хэширования пароля.
        Прямое сохранение пароля в базу данных недопустимо, так как
        он будет храниться в открытом виде.

        Args:
            validated_data (dict): Валидированные данные из запроса.
                                   Содержит поля модели User, включая 'password'.

        Returns:
            User: Созданный объект сотрудника с зашифрованным паролем.
        """
        # Извлекаем пароль из данных, чтобы не передавать его напрямую в User.objects.create
        password = validated_data.pop('password', None)

        # Создаем объект пользователя
        user = User.objects.create(**validated_data)

        # Если пароль был передан, хэшируем его и сохраняем
        if password:
            user.set_password(password)
            user.save()

        return user