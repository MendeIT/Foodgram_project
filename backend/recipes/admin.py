from django.contrib import admin

from recipes.models import (Favorites,
                            Ingredient,
                            Recipe,
                            ShoppingCart,
                            Tag)


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ['name', 'measurement_unit']
    list_display_links = ['name']
    search_fields = ['name']
    ordering = ['name']
    list_per_page = 10


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ['name', 'color', 'slug']
    list_display_links = ['name']
    search_fields = ['name']
    ordering = ['name']
    prepopulated_fields = {'slug': ['name']}


@admin.register(Favorites)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe']
    search_fields = ['user__username', 'recipe__name']
    ordering = ['user']
    raw_id_fields = ['recipe']
    list_select_related = ['user', 'recipe']


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ['user', 'recipe']
    search_fields = ['user__username', 'recipe__name']
    ordering = ['user']
    raw_id_fields = ['recipe']
    list_select_related = ['user', 'recipe']


class IngredientInline(admin.TabularInline):
    model = Recipe.ingredients.through


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'author', 'favorites_counter', 'shoppingcart_counter'
    ]
    list_display_links = ['name']
    list_filter = ['tags']
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

    @admin.display(
        description='Кол-во добавлений рецепта в корзину'
    )
    def shoppingcart_counter(self, obj):
        return obj.shoppingcart.count()

    def get_queryset(self, request):
        qs = super(RecipeAdmin, self).get_queryset(request)

        return qs.select_related('author').prefetch_related(
            'tags', 'ingredients'
        )
