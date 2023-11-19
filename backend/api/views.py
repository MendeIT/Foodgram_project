from django_filters.rest_framework import DjangoFilterBackend
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter
from rest_framework.mixins import (CreateModelMixin,
                                   ListModelMixin,
                                   RetrieveModelMixin)
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import (GenericViewSet,
                                     ModelViewSet)

from api.filters import RecipeFilter
from api.pagination import CustomPaginator
from api.permissions import IsAuthorOrReadOnlyPermission
from api.serializers import (AuthorSerializer,
                             IngredientSerializer,
                             FollowAuthorSerializer,
                             RecipeSerializer,
                             RecipeCreateSerializer,
                             RecipeListSerializer,
                             SetPasswordSerializer,
                             TagSerializer,
                             UserListSerializer,
                             UserCreateSerializer)
from foodgram_project.settings import FILE_NAME
from recipes.models import (Ingredient,
                            Favorites,
                            Recipe,
                            RecipeIngredient,
                            ShoppingCart,
                            Tag)
from users.models import Follow, User


class UserViewSet(CreateModelMixin,
                  ListModelMixin,
                  RetrieveModelMixin,
                  GenericViewSet):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    pagination_class = CustomPaginator

    def get_serializer_class(self):

        if self.action in ['list', 'retrieve']:
            return UserListSerializer

        return UserCreateSerializer

    @action(
        detail=False,
        methods=['get'],
        pagination_class=None,
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        serializer = UserListSerializer(
            request.user, context={'request': request}
        )

        return Response(
            serializer.data,
            status=status.HTTP_200_OK
        )

    @action(
        detail=False,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def set_password(self, request):
        serializer = SetPasswordSerializer(
            request.user, data=request.data
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(
            {'detail': 'Пароль успешно изменен.'},
            status=status.HTTP_204_NO_CONTENT
        )

    @action(
        detail=False, methods=['get'],
        permission_classes=[IsAuthenticated],
        pagination_class=CustomPaginator
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(follower__user=request.user)
        page = self.paginate_queryset(queryset)
        serializer = AuthorSerializer(
            page, many=True, context={'request': request}
        )

        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, **kwargs):
        author = get_object_or_404(User, pk=kwargs['pk'])

        if request.method == 'POST':
            if author.following.filter(user=request.user).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на данного автора.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            if request.user == author:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = FollowAuthorSerializer(
                author,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Follow.objects.create(user=request.user, author=author)

            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )

        elif request.method == 'DELETE':

            if not author.following.filter(user=request.user).exists():
                return Response(
                    {'errors': 'У Вас нет подписки на данного автора.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            author.delete()

            return Response(
                {'detail': 'Успешная отписка'},
                status=status.HTTP_204_NO_CONTENT
            )


class IngredientViewSet(ListModelMixin,
                        RetrieveModelMixin,
                        GenericViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny]
    pagination_class = None
    filter_backends = [SearchFilter]
    search_fields = ['^name']


class TagViewSet(ListModelMixin,
                 RetrieveModelMixin,
                 GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny]
    pagination_class = None


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = [IsAuthorOrReadOnlyPermission]
    pagination_class = CustomPaginator
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete', 'create']

    def get_serializer_class(self):

        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer

        return RecipeCreateSerializer

    def partial_update(self, request, *args, **kwargs):

        if not Recipe.objects.filter(id=kwargs['pk']).exists():
            return Response(
                {'errors': 'Запрашиваемый рецепт отсутствует.'},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            request.data['ingredients']
            request.data['tags']
        except KeyError:
            return Response(
                {'errors': 'Рецепт не содержит "ingredients"/"tags".'},
                status=status.HTTP_400_BAD_REQUEST
            )

        return super().partial_update(request, *args, **kwargs)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthorOrReadOnlyPermission]
    )
    def favorite(self, request, **kwargs):
        if not Recipe.objects.filter(id=kwargs['pk']).exists():
            return Response(
                {'errors': (
                    'Нельзя добавить или удалить '
                    'несуществующий рецепт в избранное.'
                )},
                status=status.HTTP_400_BAD_REQUEST
            )
        recipe = Recipe.objects.get(id=kwargs['pk'])

        if request.method == 'POST':

            if recipe.favorites.filter(user=request.user).exists():
                return Response(
                    {'errors': 'Рецепт уже добавлен в избранное.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = RecipeSerializer(
                recipe,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)
            Favorites.objects.create(user=request.user, recipe=recipe)

            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )

        if request.method == 'DELETE':

            if not recipe.favorites.filter(user=request.user).exists():
                return Response(
                    {'errors': 'В Избранном нет данного рецепта.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            recipe.delete()

            return Response(
                {'detail': 'Рецепт успешно удален из избранного.'},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthorOrReadOnlyPermission],
        pagination_class=None
    )
    def shopping_cart(self, request, **kwargs):

        if not Recipe.objects.filter(id=kwargs['pk']).exists():
            return Response(
                {'errors': (
                    'Нельзя добавить или удалить '
                    'несуществующий рецепт в корзину.'
                )},
                status=status.HTTP_400_BAD_REQUEST
            )

        recipe = Recipe.objects.get(id=kwargs['pk'])

        if request.method == 'POST':

            if recipe.shoppingcart.filter(user=request.user).exists():
                return Response(
                    {'errors': 'Рецепт уже есть в списке продуктов.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            serializer = RecipeSerializer(
                recipe,
                data=request.data,
                context={"request": request}
            )

            serializer.is_valid(raise_exception=True)
            ShoppingCart.objects.create(user=request.user, recipe=recipe)

            return Response(
                serializer.data, status=status.HTTP_201_CREATED
            )

        if request.method == 'DELETE':

            if not recipe.shoppingcart.filter(user=request.user).exists():
                return Response(
                    {'errors': 'В корзине нет данного рецепта.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            recipe.delete()

            return Response(
                {'detail': 'Рецепт удален из корзины.'},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request, **kwargs):
        ingredients = (
            RecipeIngredient.objects.filter(
                recipe__shoppingcart__user=request.user
            ).values('ingredient').values_list(
                'ingredient__name',
                'amount',
                'ingredient__measurement_unit'
            )
        )
        lst_ingredients = [f'{i[0]} - {i[1]} {i[2]}.' for i in ingredients]
        file = HttpResponse(
            'Cписок покупок:\n' + '\n'.join(lst_ingredients),
            content_type='text/plain', charset='utf-8'
        )
        file['Content-Disposition'] = (f'attachment; filename={FILE_NAME}')

        return file
