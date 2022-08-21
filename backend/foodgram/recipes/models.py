from colorfield.fields import ColorField
from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Ingredient(models.Model):
    """Модель ингредиента."""
    name = models.CharField(
       max_length=200,
       verbose_name='Название ингредиента',
       db_index=True
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Единица измерения'
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    """Модель тегов"""
    name = models.CharField(
        max_length=200,
        verbose_name='Название тега',
        db_index=True
    )
    color = ColorField(
        format='hex',
        verbose_name='Код цвета'
    )
    slug = models.SlugField(
        max_length=200,
        verbose_name='Slug',
        unique=True
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.slug
