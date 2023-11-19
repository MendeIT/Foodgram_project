from django.core.validators import (MaxValueValidator,
                                    MinValueValidator,
                                    RegexValidator)
from django.db import models

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
        return f'{self.name}, {self.measurement_unit}'

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингридиенты'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_measurement_unit'
            )
        ]


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
        verbose_name='Цвет тега',
        validators=[
            RegexValidator(regex=r'^\#([a-fA-F0-9]{6})$',
                           message='Цвет не соответствует формату HEX')
        ]
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
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'color', 'slug'),
                name='unique_name_color_slug'
            )
        ]


class Recipe(models.Model):
    """
    Модель рецептов.
    """
    tags = models.ManyToManyField(
        to=Tag,
        verbose_name='Список тегов',
        related_name='recipes',
        help_text='Укажите тег'
    )
    author = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор рецепта'
    )
    ingredients = models.ManyToManyField(
        to=Ingredient,
        through='RecipeIngredient',
        related_name='recipes',
        verbose_name='Список ингредиентов'
    )
    name = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Введите название рецепта'
    )
    image = models.ImageField(
        upload_to='recipe/images/',
        default=None,
        verbose_name='Ссылка на картинку на сайте',
        help_text='Загрузите картинку'
    )
    text = models.TextField(
        verbose_name='Описание',
        help_text='Опишите рецепт приготовления'
    )
    cooking_time = models.PositiveSmallIntegerField(
        default=1,
        validators=(
            MinValueValidator(limit_value=1,
                              message='Блюдо готово!'),
            MaxValueValidator(limit_value=1_440,
                              message='Время приготовления ограничено сутками')
        ),
        verbose_name='Время приготовления в минутах',
        help_text='Укажите временя приготовления в минутах'
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации'
    )

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'author'),
                name='unique_name_author'
            )
        ]


class RecipeIngredient(models.Model):
    """
    Связующая таблица между Recipe и Ingridient.
    """
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='recipe_ingridient',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        to=Ingredient,
        on_delete=models.CASCADE,
        related_name='ingridient_recipe',
        verbose_name='Ингредиент'
    )
    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=[
            MinValueValidator(limit_value=1,
                              message='Значение должно быть больше 0'),
            MaxValueValidator(limit_value=5_000,
                              message='Увеличьте ед. изм., например 1000г=1кг')
        ]
    )

    def __str__(self):
        return f'{self.recipe} {self.ingredient} {self.amount}'

    class Meta:
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'


class Favorites(models.Model):
    """
    Модель Избранного для авторизованного пользователя.
    """
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Избранное пользователя'
    )
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт в избранном пользователя'
    )
    add_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления в избранное'
    )

    def __str__(self):
        return f'{self.user} {self.recipe}'

    class Meta:
        verbose_name = 'Избранное пользователя'
        verbose_name_plural = 'Избранное пользователя'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_favorites_recipe_user'
            )
        ]


class ShoppingCart(models.Model):
    """
    Модель корзины для авторизованного пользователя.
    """
    user = models.ForeignKey(
        to=User,
        on_delete=models.CASCADE,
        related_name='shoppingcart',
        verbose_name='Пользователь имеющий корзину'
    )
    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='shoppingcart',
        verbose_name='Рецепт в корзине пользователя'
    )
    add_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата добавления в корзину'
    )

    def __str__(self):
        return f'{self.user} {self.recipe}'

    class Meta:
        verbose_name = 'Корзина пользователя'
        verbose_name_plural = 'Корзина пользователя'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_shoppingcard_recipe_user'
            )
        ]
