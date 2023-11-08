from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import Ingredient, Tag, Recipe, RecipeIngredient
from users.models import User


class UserListSerializer(UserSerializer):
    """
    Сериализатор пользователей.
    """
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed'
        ]

    def get_is_subscribed(self, data: User) -> bool:
        user = self.context['request'].user

        if user.is_anonymous or user == data:
            return False

        return user.follower.filter(author=data).exists()


class UserCreateSerializer(UserCreateSerializer):
    """
    Сериализатор создания пользователя.
    """
    class Meta:
        model = User
        fields = [
            'id',
            'email',
            'username',
            'first_name',
            'last_name',
            'password'
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
        }

    def validate(self, data) -> dict:
        for i in data:
            if data[i] == '':
                raise serializers.ValidationError(
                    {'error': 'Заполните все поля'}
                )

        if data['username'] == data['password']:
            raise serializers.ValidationError(
                {'password': 'Имя пользователя и пароль не должны совпадать!'}
            )

        elif data['first_name'] == data['last_name']:
            raise serializers.ValidationError(
                {'last_name': 'Имя и Фамилия не должны совпадать!'}
            )

        return data


class SetPasswordSerializer(serializers.Serializer):
    """
    Изменение пароля пользователя.
    """
    current_password = serializers.CharField()
    new_password = serializers.CharField()

    def validate_new_password(self, value):
        try:
            validate_password(value)
        except exceptions.ValidationError as error:
            raise serializers.ValidationError(
                {'new_password': list(error.messages)}
            )

        return value

    def update(self, instance, validated_data):
        if not instance.check_password(validated_data['current_password']):
            raise serializers.ValidationError(
                {'current_password': 'Не верный текущий пароль.'}
            )

        if (validated_data['current_password'] ==
                validated_data['new_password']):
            raise serializers.ValidationError(
                {'new_password': 'Пароль должен отличаться от текущего.'}
            )

        instance.set_password(validated_data['new_password'])
        instance.save()

        return validated_data


class RecipeSerializer(serializers.ModelSerializer):
    """
    Сериализатор рецептов без игредиентов.
    """
    name = serializers.ReadOnlyField()
    image = Base64ImageField(read_only=True)
    cooking_time = serializers.ReadOnlyField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'name',
            'image',
            'cooking_time'
        ]


class AuthorSerializer(serializers.ModelSerializer):
    """
    Сериализатор авторов.
    """
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        ]

    def get_is_subscribed(self, data: User) -> bool:
        user = self.context['request'].user

        if user.is_anonymous or user == data:
            return False

        return user.follower.filter(author=data).exists()

    def get_recipes_count(self, data):
        return data.recipes.count()

    def get_recipes(self, data):
        request = self.context['request']
        limit = request.GET['recipes_limit']
        recipes = data.recipes.all()

        if limit:
            recipes = recipes[:int(limit)]
        serializer = RecipeSerializer(recipes, many=True, read_only=True)

        return serializer.data


class FollowAuthorSerializer(serializers.ModelSerializer):
    """
    Сериализатор подписки и отписки.
    """
    email = serializers.ReadOnlyField()
    username = serializers.ReadOnlyField()
    is_subscribed = serializers.SerializerMethodField()
    recipes = RecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count'
        ]

    def get_is_subscribed(self, data: User) -> bool:
        user = self.context['request'].user

        if user.is_anonymous or user == data:
            return False

        return user.follower.filter(author=data).exists()

    def get_recipes_count(self, data):
        return data.recipes.count()

    def validate(self, data):
        if self.context['request'].user == data:
            raise serializers.ValidationError(
                {'errors': 'Нельзя подписаться на себя!'}
            )

        return data


class TagSerializer(serializers.ModelSerializer):
    """
    Сериализатор Тегов.
    """
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ['__all__']


class IngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор Ингредиентов.
    """
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ['__all__']


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """
    Сериализатор списка ингредиентов для рецепта.
    """
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = [
            'id',
            'name',
            'measurement_unit',
            'amount'
        ]
        read_only_fields = ['amount']


class RecipeListSerializer(serializers.ModelSerializer):
    """
    Сериализатор список рецептов.
    """
    author = UserListSerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    ingredients = RecipeIngredientSerializer(many=True,
                                             read_only=True,
                                             source='recipes')
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time'
        ]

    def get_is_favorited(self, data):
        user = self.context['request'].user

        if user.is_anonymous or user == data:
            return False

        return user.favorites.filter(recipe=data).exists()

    def get_is_in_shopping_cart(self, data):
        user = self.context['request'].user

        if user.is_anonymous or user == data:
            return False

        return user.shoppingcard.filter(recipe=data).exists()


class RecipeIngredientCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор ингредиента под создание рецепта.
    """
    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class RecipeCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор для создания, изменения или удаления рецепта.
    """
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    author = UserListSerializer(read_only=True)
    id = serializers.ReadOnlyField()
    ingredients = RecipeIngredientCreateSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = [
            'id',
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
            'author'
        ]
        extra_kwargs = {
            'ingredients': {'required': True},
            'tags': {'required': True},
            'name': {'required': True},
            'text': {'required': True},
            'image': {'required': True},
            'cooking_time': {'required': True},
        }

    def validate(self, data):
        if not data['tags']:
            raise serializers.ValidationError(
                {'tags': 'Укажите тег.'}
            )

        if not data['ingredients']:
            raise serializers.ValidationError(
                {'ingredients': 'Укажите ингридиенты.'}
            )

        ingridients_list = [i['id'] for i in data['ingredients']]
        ingridients_list_uniqum = set(ingridients_list)

        if not len(ingridients_list) == len(ingridients_list_uniqum):
            raise serializers.ValidationError(
                {'ingredients': 'Ингридиенты не должны дублироваться.'}
            )

        return data

    def set_tags_ingredients(self, recipe, tags, ingredients):
        recipe.tags.set(tags)
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                recipe=recipe,
                ingredient=Ingredient.objects.get(pk=i['id']),
                amount=i['amount']
            ) for i in ingredients]
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        self.set_tags_ingredients(recipe, tags, ingredients)

        return recipe

    def update(self, instance, validated_data):
        instance.image = validated_data.get('image', instance.image)
        instance.name = validated_data.get('name', instance.name)
        instance.text = validated_data.get('text', instance.text)
        instance.cooking_time = validated_data.get(
            'cooking_time', instance.cooking_time
        )
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')
        RecipeIngredient.objects.filter(
            recipe=instance,
            ingredient__in=instance.ingredients.all()
        ).delete()
        self.set_tags_ingredients(instance, tags, ingredients)
        instance.save()

        return instance

    def to_representation(self, value):
        return RecipeListSerializer(value, context=self.context).data
