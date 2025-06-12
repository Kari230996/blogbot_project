from django.db import models
from django.contrib.auth.models import User


class Post(models.Model):
    title = models.CharField(max_length=50, verbose_name="Заголовок")
    content = models.TextField(blank=True, verbose_name="Текст")
    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Дата создания")
    owner = models.ForeignKey(User, on_delete=models.CASCADE,
                              related_name="posts", null=True, blank=True, verbose_name="Пользователь")

    def __str__(self):
        return f"{self.title} (#{self.id})"

    class Meta:
        verbose_name = "Пост"
        verbose_name_plural = "Посты"
        ordering = ["-created_at"]
