from rest_framework.decorators import action
from rest_framework.mixins import (CreateModelMixin,
                                   ListModelMixin,
                                   RetrieveModelMixin)
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.viewsets import GenericViewSet, ModelViewSet, ReadOnlyModelViewSet

from api.serializers import (FollowSerializer,
                             IngredientSerializer,
                             RecipeSerializer,
                             TagSerializer,
                             UserListSerializer,
                             UserCreateSerializer)
from recipes.models import Ingredient, Recipe, Tag
from users.models import Follow, User


class UserListViewSet(CreateModelMixin,
                      ListModelMixin,
                      RetrieveModelMixin,
                      GenericViewSet):
    queryset = User.objects.all()
    serializer_class = UserListSerializer
    pagination_class = LimitOffsetPagination

    def get_serializer_class(self):
        if self.action == ('list', 'retrieve'):
            return UserListSerializer
        return UserCreateSerializer


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = RecipeSerializer
    pagination_class = LimitOffsetPagination


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    pagination_class = LimitOffsetPagination


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = LimitOffsetPagination


class FollowViewSet(ModelViewSet):
    queryset = Follow.objects.all()
    serializer_class = FollowSerializer
    pagination_class = LimitOffsetPagination
