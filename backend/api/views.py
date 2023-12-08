from django.conf import settings
from django.db import IntegrityError
from django.db.models import Sum, Count
from django_filters.rest_framework import DjangoFilterBackend
from django.http import FileResponse, Http404
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
            serializer.data, status=status.HTTP_200_OK
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
        queryset = User.objects.filter(
            following__user=request.user
        ).annotate(
            recipes_count=Count('recipes')
        )

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
        author = self.get_object()

        if request.method == 'POST':

            if request.user == author:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            serializer = FollowAuthorSerializer(
                author, data=request.data, context={'request': request}
            )
            serializer.is_valid(raise_exception=True)

            try:
                Follow.objects.create(user=request.user, author=author)
            except IntegrityError:
                return Response(
                    {'errors': 'Вы уже подписаны на данного автора.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )

        elif request.method == 'DELETE':
            number_of_objects_removed, _ = author.following.filter(
                user=request.user
            ).delete()

            if number_of_objects_removed == 0:
                return Response(
                    {'errors': 'У Вас нет подписки на данного автора.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response(
                {'detail': 'Успешная отписка.'},
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
    """Модель представления рецептов."""

    queryset = Recipe.objects.select_related(
        'author').prefetch_related('tags', 'ingredients')
    permission_classes = [IsAuthorOrReadOnlyPermission]
    pagination_class = CustomPaginator
    filter_backends = [DjangoFilterBackend, SearchFilter]
    filterset_class = RecipeFilter
    http_method_names = ['get', 'post', 'patch', 'delete', 'create']

    def get_serializer_class(self):

        if self.action in ('list', 'retrieve'):
            return RecipeListSerializer

        return RecipeCreateSerializer

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, **kwargs):
        try:
            recipe = self.get_object()
        except Http404:
            if request.method == 'POST':
                return Response({
                    'errors': (
                        'Нельзя добавить '
                        'несуществующий рецепт в избранное.'
                    )
                },
                    status=status.HTTP_400_BAD_REQUEST
                )
            raise Http404

        if request.method == 'POST':
            serializer = RecipeSerializer(
                recipe,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)

            try:
                Favorites.objects.create(user=request.user, recipe=recipe)
            except IntegrityError:
                return Response(
                    {'errors': 'Рецепт уже добавлен в избранное.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )

        if request.method == 'DELETE':
            number_of_objects_removed, _ = recipe.favorites.filter(
                user=request.user
            ).delete()

            if number_of_objects_removed == 0:
                return Response(
                    {'errors': 'В Избранном нет данного рецепта.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response(
                {'detail': 'Рецепт успешно удален из избранного.'},
                status=status.HTTP_204_NO_CONTENT
            )

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated],
        pagination_class=None
    )
    def shopping_cart(self, request, **kwargs):
        try:
            recipe = self.get_object()
        except Http404:
            if request.method == 'POST':
                return Response({
                    'errors': (
                        'Нельзя добавить '
                        'несуществующий рецепт в корзину.'
                    )
                },
                    status=status.HTTP_400_BAD_REQUEST
                )
            raise Http404

        if request.method == 'POST':
            serializer = RecipeSerializer(
                recipe,
                data=request.data,
                context={'request': request}
            )
            serializer.is_valid(raise_exception=True)

            try:
                ShoppingCart.objects.create(user=request.user, recipe=recipe)
            except IntegrityError:
                return Response(
                    {'errors': 'Рецепт уже есть в списке продуктов.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            else:
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )

        if request.method == 'DELETE':
            number_of_objects_removed, _ = recipe.shoppingcart.filter(
                user=request.user
            ).delete()

            if number_of_objects_removed == 0:
                return Response(
                    {'errors': 'В корзине нет данного рецепта.'},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response(
                {'detail': 'Рецепт удален из корзины.'},
                status=status.HTTP_204_NO_CONTENT
            )

    def create_file_txt_for_download(self, ingredients):
        formatted_list_ingredients = [
            f'{ingredient[0]} --- {ingredient[1]} {ingredient[2]}.'
            for ingredient in ingredients
        ]
        text_for_download = 'Cписок покупок:\n' + '\n'.join(
            formatted_list_ingredients
        )

        return FileResponse(
            text_for_download,
            as_attachment=True,
            filename=settings.FILE_NAME,
            headers={'Content-Type': 'text/plain'}
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
            ).values('ingredient').annotate(
                total_amount=Sum('amount')
            ).values_list(
                'ingredient__name',
                'total_amount',
                'ingredient__measurement_unit'
            )
        )

        return self.create_file_txt_for_download(ingredients)
