from django.db import models

from recipes.managers import (FavoritedManager,
                              FavoritedStatus,
                              ShoppingManager,
                              ShoppingStatus)
from users.models import User


class Ingredient(models.Model):
    """
    Модель ингредиетов.
    """
    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Еденица измерения'
    )

    def __str__(self):
        return f'{self.name} измеряется в "{self.measurement_unit}"'

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингридиенты'


class Tag(models.Model):
    """
    Модель тегов.
    """
    name = models.CharField(
        max_length=200,
        verbose_name='Имя тега'
    )
    color = models.CharField(
        max_length=7,
        verbose_name='Цвет тега'
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        db_index=True,
        verbose_name='Слаг тега'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'


class Recipe(models.Model):
    """Модель рецептов."""

    tag = models.ManyToManyField(
        Tag,
        through='TagRecipe',
        verbose_name='Список тегов'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    ingredients = models.ManyToManyField(
        to=Ingredient,
        related_name='recipes',
        verbose_name='Список ингредиентов'
    )
    is_favorited = models.BooleanField(
        choices=FavoritedStatus.choices,
        default=FavoritedStatus.UNFAVORITED,
        verbose_name='Находится ли в избранном'
    )
    is_in_shopping_cart = models.BooleanField(
        choices=ShoppingStatus.choices,
        default=ShoppingStatus.OUTBASKET,
        verbose_name='Находится ли в корзине'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название'
    )
    image = models.ImageField(
        upload_to='recipe/images/',
        blank=True,
        null=True,
        default=None,
        verbose_name='Ссылка на картинку на сайте'
    )
    text = models.TextField(
        verbose_name='Описание'
    )
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    objects = models.Manager()
    favorited = FavoritedManager()
    inbasket = ShoppingManager()

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'


class Follow(models.Model):
    """
    Модель подписчиков.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписчик'
        verbose_name_plural = 'Подписчики'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author'),
                name='unique_follow'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'


class TagRecipe(models.Model):
    tag = models.ForeignKey(
        to=Tag,
        on_delete=models.CASCADE,
        blank=True,
        null=True
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('tag', 'recipe'),
                name='unique_tagrecipe'
            )
        ]

    def __str__(self):
        return f'{self.tag} {self.recipe}'
