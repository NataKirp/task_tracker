from django.test import TestCase

from .models import Position, User


class UserModelTests(TestCase):
    """
    Тесты для кастомной модели User и справочника Position.
    """

    def setUp(self):
        """
        Метод setUp выполняется ПЕРЕД каждым тестом.
        Создаем базовые объекты, чтобы не дублировать код.
        """
        self.position = Position.objects.create(name="Разработчик")
        self.user = User.objects.create_user(
            username="testuser",
            password="testpassword",
            first_name="Иван",
            last_name="Иванов",
            position=self.position,
        )

    def test_position_str(self):
        """Проверяем, что __str__ у должности возвращает её название."""
        self.assertEqual(str(self.position), "Разработчик")

    def test_user_str_with_full_name(self):
        """Проверяем, что __str__ пользователя возвращает ФИО, если оно заполнено."""
        # Ожидаем "Иван Иванов" (first_name + last_name)
        self.assertEqual(str(self.user), "Иван Иванов")

    def test_user_str_without_full_name(self):
        """Проверяем, что __str__ возвращает username, если ФИО не заполнено."""
        user_without_name = User.objects.create_user(
            username="noname", password="testpassword"
        )
        self.assertEqual(str(user_without_name), "noname")

    def test_user_position_relation(self):
        """Проверяем, что связь с должностью работает корректно."""
        self.assertEqual(self.user.position, self.position)
        self.assertEqual(self.user.position.name, "Разработчик")
