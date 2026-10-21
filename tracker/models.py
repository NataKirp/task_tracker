from django.db import models
from django.conf import settings


class Task(models.Model):
    """
    Модель задачи.
    """
    STATUS_CHOICES = [
        ('new', 'Новая'),
        ('in_progress', 'В работе'),
        ('done', 'Выполнена'),
    ]

    name = models.CharField(
        max_length=255,
        verbose_name="Наименование"
    )

    parent_task = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='subtasks',
        verbose_name="Родительская задача"
    )

    assignee = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='tasks',
        verbose_name="Исполнитель"
    )

    due_date = models.DateField(
        verbose_name="Срок"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name="Статус"
    )

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ['due_date']  # По умолчанию сортируем по сроку

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        """
        Добавляет логику каскадного закрытия родительской задачи.
        """
        super().save(*args, **kwargs)

        if self.status == 'done' and self.parent_task:
            parent = self.parent_task
            has_subtasks = parent.subtasks.exists()

            if has_subtasks:
                all_done = not parent.subtasks.exclude(status='done').exists()
                if all_done and parent.status != 'done':
                    parent.status = 'done'
                    parent.save()
