from django.db import models


class FavoritedStatus(models.IntegerChoices):
    UNFAVORITED = 0, 'Не изрбранное'
    FAVORITED = 1, 'Избранное'


class FavoritedManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            is_favorited=FavoritedStatus.FAVORITED
        )


class ShoppingStatus(models.IntegerChoices):
    OUTBASKET = 0, 'Не в корзине'
    INBASKET = 1, 'В корзине'


class ShoppingManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(
            is_in_shopping_cart=ShoppingStatus.INBASKET
        )
