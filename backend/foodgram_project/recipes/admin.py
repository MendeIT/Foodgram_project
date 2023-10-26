from django.contrib import admin

from recipes.models import Recipe, Follow, Ingredients


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'text', 'pub_date', 'author')
    search_fields = ('name',)
    list_filter = ('pub_date',)
    empty_value_display = '-пусто-'


class FollowAdmin(admin.ModelAdmin):
    list_display = ('author', 'user')
    search_fields = ('author',)
    list_filter = ('author',)
    list_editable = ('user',)
    empty_value_display = '-пусто-'


class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name', 'measurement_unit')
    search_fields = ('name',)
    list_filter = ('name',)
    list_editable = ('measurement_unit',)
    empty_value_display = '-пусто-'


admin.site.register(Recipe, RecipeAdmin)

admin.site.register(Ingredients, IngredientsAdmin)

admin.site.register(Follow, FollowAdmin)
