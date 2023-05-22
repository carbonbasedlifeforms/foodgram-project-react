from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models


class User(AbstractUser):
    """Кастомизированная модель User"""
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name', 'password']
    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=settings.EMAIL_MAX_LENGTH,
        db_index=True,
        unique=True,
        blank=False,
    )
    username = models.CharField(
        verbose_name='Уникальный юзернейм',
        max_length=settings.NAMES_MAX_LENGTH,
        db_index=True,
        unique=True,
        blank=False,
    )
    first_name = models.CharField(
        verbose_name='Имя',
        max_length=settings.NAMES_MAX_LENGTH,
        blank=False,
        null=False,
    )
    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=settings.NAMES_MAX_LENGTH,
        blank=False,
        null=False
    )

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.username


class Follow(models.Model):
    """Модель подписок на других пользователей"""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow'
            ),
            models.CheckConstraint(
                check=models.Q(user=models.F('user')),
                name='check_self_follow'
            )
        ]
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user_id} {self.subscribe_id}'
