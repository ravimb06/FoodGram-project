from tabnanny import verbose
from django.contrib.auth.models import AbstractUser
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.db import models

USER = 'user'
ADMIN = 'admin'


class User(AbstractUser):
    """Модель пользователей."""
    ROLES = (
        (USER, USER),
        (ADMIN, ADMIN),
    )
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[username_validator],
        verbose_name='Имя пользователя'
    )
    first_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Имя',
    )
    last_name = models.CharField(
        max_length=150,
        blank=True,
        verbose_name='Фамилия',
    )
    email = models.EmailField(
        max_length=254,
        unique=True,
        verbose_name='email',
    )
    role = models.CharField(
        choices=ROLES,
        max_length=25,
        default=USER,
        verbose_name='Роль пользователя'
    )

    REQUIRED_FIELDS = ['email']
    USERNAME_FIELD = 'email'

    class Meta:
        ordering = (id,)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return str(self.username)

    @property
    def is_admin(self):
        return self.role == ADMIN or self.is_superuser

    @property
    def is_user(self):
        return self.role == USER


class Follow(models.Model):
    """Модель подписок."""
    user = models.models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик',
        verbose_name_plural='Подписчики',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор рецепта',
        verbose_name_plural='Авторы рецепта',
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'

    def __str__(self):
        return f'{self.user} подписан на {self.author}.'
