from django.contrib import admin

from recipes.models import (Favorites,
                            Ingredient,
                            Recipe,
                            RecipeIngredient,
                            ShoppingCart,
                            Tag)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'measurement_unit']
    list_display_links = ['name']
    list_editable = ['measurement_unit']
    search_fields = ['name']
    ordering = ['name']
    list_per_page = 10


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'slug']
    list_display_links = ['name']
    ordering = ['name']
    prepopulated_fields = {'slug': ['name']}


@admin.register(RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ['recipe', 'ingredient', 'amount']
    list_display_links = ['recipe']
    list_editable = ['ingredient', 'amount']
    list_filter = ['recipe']
    ordering = ['recipe']
    search_fields = ['recipe__name', 'ingredient__name']
    list_select_related = ['recipe', 'ingredient']
    list_per_page = 10


@admin.register(Favorites)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe']
    search_fields = ['user__username', 'recipe__name']
    list_filter = ['user']
    ordering = ['user']
    raw_id_fields = ['recipe']
    list_select_related = ['user', 'recipe']


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe']
    search_fields = ['user__username', 'recipe__name']
    list_filter = ['user']
    ordering = ['user']
    raw_id_fields = ['recipe']
    list_select_related = ['user', 'recipe']


class IngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ['name', 'author', 'favorites_counter']
    list_display_links = ['name']
    list_filter = ['name', 'author', 'tags']
    search_fields = ['name', 'author__username']
    date_hierarchy = 'pub_date'
    inlines = [IngredientInline]
    filter_horizontal = ['ingredients']
    list_per_page = 10

    @admin.display(
        description='Кол-во добавлений рецепта в избранное'
    )
    def favorites_counter(self, obj):
        return obj.favorites.count()

    def get_queryset(self, request):
        qs = super(RecipeAdmin, self).get_queryset(request)

        return qs.select_related('author').prefetch_related(
            'tags', 'ingredients'
        )
