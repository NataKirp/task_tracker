from django.contrib.auth.models import AbstractUser
from django.db import models

class Position(models.Model):
    """
    Справочник должностей.
    """
    name = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="Название должности"
    )

    class Meta:
        verbose_name = "Должность"
        verbose_name_plural = "Должности"
        ordering = ['name']

    def __str__(self):
        return self.name


class User(AbstractUser):
    """
    Кастомная модель пользователя (Сотрудника).
    """
    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='users',
        verbose_name="Должность"
    )

    class Meta:
        verbose_name = "Сотрудник"
        verbose_name_plural = "Сотрудники"

    def __str__(self):
        return self.get_full_name() or self.username
