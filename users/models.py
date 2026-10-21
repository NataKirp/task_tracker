from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """
    Кастомная модель пользователя.
    """
    position = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name="Должность"
    )

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def __str__(self):
        return self.get_full_name() or self.username