from django.core.validators import (MaxValueValidator,
                                    MinValueValidator)
from django.db import models

from colorfield.fields import ColorField

from users.models import User


class Ingredient(models.Model):
    """Модель ингредиетов."""

    name = models.CharField(
        max_length=200,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=200,
        verbose_name='Еденица измерения'
    )

    class Meta:
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit'),
                name='unique_name_measurement_unit',
                violation_error_message=(
                    'Ингредиент уже имеется в БД, если вы хотите '
                    'изменить еденицу измерения, необходимо '
                    'внести корректировки в файл CSV.'
                )
            )
        ]
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингридиенты'

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Tag(models.Model):
    """Модель тегов."""

    COLOR_PALETTE = [
        ('#c45824', 'терракотовый', ),
        ('#4b0082', 'индиго', ),
        ('#FF7F50', 'коралловый', ),
        ('#009B77', 'изумруд', ),
    ]

    name = models.CharField(
        max_length=200,
        verbose_name='Имя тега'
    )
    color = ColorField(format='hex', samples=COLOR_PALETTE)
    slug = models.SlugField(
        max_length=200,
        unique=True,
        db_index=True,
        verbose_name='Слаг тега',
        error_messages={
            'unique': 'Вводимый slug уже имеется.',
        }
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'color', 'slug'),
                name='unique_name_color_slug',
                violation_error_message=(
                    'Тег с выбранным цветом slug уже существует, '
                    'введите другой тег с другим цветом и другим slug.'
                )
            )
        ]
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    """Модель рецептов."""

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

    class Meta:
        ordering = ['-pub_date']
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'author'),
                name='unique_name_author',
                violation_error_message=(
                    'Вы уже создавали рецепт с таким названием'
                )
            )
        ]
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Связующая таблица между Recipe и Ingridient."""

    recipe = models.ForeignKey(
        to=Recipe,
        on_delete=models.CASCADE,
        related_name='ingredient',
        verbose_name='Рецепт'
    )
    ingredient = models.ForeignKey(
        to=Ingredient,
        on_delete=models.CASCADE,
        related_name='recipe',
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

    class Meta:
        verbose_name = 'Ингредиенты в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return f'{self.recipe} {self.ingredient} {self.amount}'


class Favorites(models.Model):
    """Модель Избранного для авторизованного пользователя."""

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

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_favorites_recipe_user',
                violation_error_message='Рецепт уже в Избранном'
            )
        ]
        verbose_name = 'Избранное пользователя'
        verbose_name_plural = 'Избранное пользователя'

    def __str__(self):
        return f'{self.user} {self.recipe}'


class ShoppingCart(models.Model):
    """Модель корзины для авторизованного пользователя."""

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

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'user'],
                name='unique_shoppingcard_recipe_user',
                violation_error_message='Рецепт уже в Корзине'
            )
        ]
        verbose_name = 'Корзина пользователя'
        verbose_name_plural = 'Корзина пользователя'

    def __str__(self):
        return f'{self.user} {self.recipe}'
