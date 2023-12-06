from django.contrib import admin

from recipes.models import (Favorites,
                            Ingredient,
                            Recipe,
                            RecipeIngredient,
                            ShoppingCart,
                            Tag)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'measurement_unit']
    list_display_links = ['name']
    list_editable = ['measurement_unit']
    search_fields = ['name']
    ordering = ['name']
    list_per_page = 10


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'color', 'slug']
    list_editable = ['name', 'color', 'slug']
    ordering = ['name']
    prepopulated_fields = {'slug': ['name']}


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ['id', 'recipe', 'ingredient', 'amount']
    list_display_links = ['recipe']
    list_editable = ['ingredient', 'amount']
    ordering = ['recipe']
    search_fields = ['recipe']
    list_select_related = ['recipe', 'ingredient']
    list_per_page = 10


@admin.register(Favorites)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'recipe']
    search_fields = ['user', 'recipe']
    list_filter = ['user']
    ordering = ['user']
    list_select_related = ['user', 'recipe']


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'recipe']
    search_fields = ['user', 'recipe']
    list_filter = ['user']
    ordering = ['user']
    list_select_related = ['user', 'recipe']


class IngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'text', 'pub_date', 'author']
    list_display_links = ['name']
    list_filter = ['pub_date']
    search_fields = ['name', 'author']
    date_hierarchy = 'pub_date'
    inlines = [IngredientInline]
    filter_horizontal = ['ingredients']
    list_per_page = 10

    def get_queryset(self, request):
        qs = super(RecipeAdmin, self).get_queryset(request)

        return qs.select_related('author').prefetch_related(
            'tags', 'ingredients'
        )
