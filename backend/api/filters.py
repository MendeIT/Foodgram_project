from django_filters.rest_framework import filters, FilterSet

from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all(),
    )
    is_favorited = filters.BooleanFilter(
        method='filter_favorited',
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='filter_shopping_cart',
    )

    class Meta:
        model = Recipe
        fields = ['tags', 'author']

    def filter_favorited(self, queryset, name, value):
        user = self.request.user

        return queryset.filter(
            favorites__user=user
        ) if value and user.is_authenticated else queryset

    def filter_shopping_cart(self, queryset, name, value):
        user = self.request.user

        return queryset.filter(
            shoppingcart__user=user
        ) if value and user.is_authenticated else queryset
