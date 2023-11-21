from django.contrib import admin

from recipes.models import (Favorites,
                            Ingredient,
                            Recipe,
                            RecipeIngredient,
                            ShoppingCart,
                            Tag)
from users.models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'first_name', 'last_name',
                    'email', 'password', 'date_joined')
    search_fields = ('username', 'first_name', 'last_name', 'email')
    list_editable = ('password',)
    list_filter = ('id',)


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('author', 'user')
    search_fields = ('author', 'user')


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_editable = ('measurement_unit',)
    empty_value_display = '-пусто-'
    ordering = ('name',)


class IngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'text', 'pub_date', 'author')
    search_fields = ('name', 'author')
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'
    inlines = (IngredientInline,)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug')
    list_editable = ('name', 'color', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    ordering = ('name',)


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipe', 'ingredient', 'amount')
    list_editable = ('recipe', 'ingredient', 'amount')


@admin.register(Favorites)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user',)
    ordering = ('user',)


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe')
    search_fields = ('user', 'recipe')
    list_filter = ('user',)
    ordering = ('user',)
