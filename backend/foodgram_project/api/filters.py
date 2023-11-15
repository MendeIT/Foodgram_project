from django_filters.rest_framework import filters, FilterSet

from recipes.models import Recipe, Tag


class RecipeFilter(FilterSet):
    tags = filters.ModelMultipleChoiceFilter(
        field_name='tags__slug',
        to_field_name='slug',
        queryset=Tag.objects.all()
    )
    is_favorited = filters.BooleanFilter(
        method='is_favorited_filter'
    )
    is_in_shopping_cart = filters.BooleanFilter(
        method='is_in_shopping_cart_filter'
    )

    class Meta:
        model = Recipe
        fields = ['tags', 'author']

    def is_favorited_filter(self, queryset, name, value):
        user = self.request.user
        limit = self.request.GET.get('is_favorited')

        if value and user.is_authenticated:
            return queryset.filter(favorites__user=user)[:int(limit)]

        return queryset

    def is_in_shopping_cart_filter(self, queryset, name, value):
        user = self.request.user
        limit = self.request.GET.get('is_in_shopping_cart')

        if value and user.is_authenticated:
            return queryset.filter(shoppingcart__user=user)[:int(limit)]

        return queryset
