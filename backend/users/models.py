from django.contrib.auth.models import AbstractUser, UserManager
from django.core.validators import EmailValidator, RegexValidator
from django.db import models


class User(AbstractUser):
    """Пользователь Foodgram."""

    password = models.CharField(
        verbose_name='Пароль',
        max_length=150,
        help_text='Введите пароль'
    )

    email = models.EmailField(
        verbose_name='Адрес электронной почты',
        max_length=254,
        unique=True,
        help_text='Введите электронную почту',
        validators=[
            EmailValidator(
                message=('Введите валидную электронну почту, '
                         'например "name@domain.com".')
            )
        ],
        error_messages={
            'unique': 'Вводимая электронная почта уже зарегистрирована.',
        }
    )

    username = models.CharField(
        verbose_name='Имя пользователя',
        max_length=150,
        unique=True,
        help_text='Введите имя пользователя/логин',
        validators=[
            RegexValidator(
                regex=r'^[a-zA-Z\d._@\+\-]+$',
                message=('Имя пользователя на латинице. '
                         'Максимальная длинна - 150 символов, '
                         'допустимые символы: "@", ".", "+", "-", "_".')
            )
        ],
        error_messages={
            'unique': 'Пользователь с таким именем уже существует.',
        }
    )

    first_name = models.CharField(
        verbose_name='Имя',
        max_length=150,
        help_text='Введите имя',
        validators=[
            RegexValidator(
                regex=r'^[А-Я][-а-яёЁ]+$',
                message='Имя с большой буквы на кириллицы.'
            )
        ]
    )

    last_name = models.CharField(
        verbose_name='Фамилия',
        max_length=150,
        help_text='Введите фамилию',
        validators=[
            RegexValidator(
                regex=r'^[А-Я][-а-яёЁ]+$',
                message='Фамилия с большой буквы на кириллицы.'
            )
        ]
    )

    password = models.CharField(
        verbose_name='Пароль',
        max_length=150,
        help_text='Введите пароль'
    )

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [
            models.UniqueConstraint(
                fields=('email', 'username'),
                name='unique_username_email',
                violation_error_message=(
                    'Данный email уже зарегестрирован с таким логином'
                )
            )
        ]

    def __str__(self):
        return (f'{self.first_name} {self.last_name} '
                f'({self.username} - {self.email})')


class Follow(models.Model):
    """Модель подписчиков."""

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
                name='unique_follow',
                violation_error_message='Вы уже подписаны на данного автора'
            )
        ]

    def __str__(self):
        return f'{self.user} подписан на {self.author}'
