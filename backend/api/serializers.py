from django.contrib.auth.password_validation import validate_password
from django.core import exceptions
from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers, status
from rest_framework.validators import UniqueTogetherValidator

from recipes.models import Ingredient, Tag, Recipe, RecipeIngredient
from users.models import User


class UserListSerializer(UserSerializer):
    """Сериализатор пользователей."""

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

    def get_is_subscribed(self, data):
        request = self.context.get('request')
        user = request.user

        if user.is_anonymous or user == data:
            return False

        return user.follower.filter(author=data).exists()


class UserCreateSerializer(UserCreateSerializer):
    """Сериализатор создания пользователя."""

    class Meta:
        model = User
        fields = [
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password'
        ]
        validators = [
            UniqueTogetherValidator(
                queryset=User.objects.all(),
                fields=['email', 'username'],
                message='Пользователь с такми логином уже существует.'
            )
        ]
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
        }

    def validate_email(self, email):
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError(
                {'email': 'Данный email уже зарегистрирован.'}
            )

        return email

    def validate(self, data):
        fields = ['email', 'username', 'first_name', 'last_name', 'password']
        for field in fields:
            if field not in data:
                raise serializers.ValidationError(
                    {f'{field}': f'{field} обязательно к заполнению.'}
                )

        if data['username'] == data['password']:
            raise serializers.ValidationError(
                {'password': 'Имя пользователя и пароль не должны совпадать.'}
            )

        if data['first_name'] == data['last_name']:
            raise serializers.ValidationError(
                {'last_name': 'Имя и Фамилия не должны совпадать.'}
            )

        return super().validate(data)


class SetPasswordSerializer(serializers.Serializer):
    """Изменение пароля пользователя."""

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

        if (validated_data['current_password']
                == validated_data['new_password']):
            raise serializers.ValidationError(
                {'new_password': 'Пароль должен отличаться от текущего.'}
            )

        instance.set_password(validated_data['new_password'])
        instance.save()

        return validated_data


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецептов без игредиентов."""

    image = Base64ImageField(read_only=True)

    class Meta:
        model = Recipe
        fields = ['id', 'name', 'image', 'cooking_time']
        read_only_fields = ['name', 'cooking_time']


class AuthorSerializer(serializers.ModelSerializer):
    """Сериализатор авторов."""

    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.ReadOnlyField()

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

    def get_is_subscribed(self, data):
        user = self.context.get('request').user

        if user.is_anonymous or user == data:
            return False

        return user.follower.filter(author=data).exists()

    def get_recipes(self, data):
        request = self.context.get('request')
        limit = (False if request.GET is None
                 else request.GET.get('recipes_limit'))
        recipes_all = data.recipes.all()
        recipes = recipes_all[:int(limit)] if limit else recipes_all

        serializer = RecipeSerializer(
            recipes, many=True, read_only=True
        )

        return serializer.data


class FollowAuthorSerializer(serializers.ModelSerializer):
    """Сериализатор подписки и отписки."""

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
        read_only_fields = ['email', 'username', 'first_name', 'last_name']

    def get_is_subscribed(self, data):
        user = self.context.get('request').user

        if user.is_anonymous or user == data:
            return False

        return user.follower.filter(author=data).exists()

    def get_recipes(self, data):
        request = self.context.get('request')
        limit = request.GET.get('recipes_limit')
        recipes_all = data.recipes.all()
        recipes = recipes_all[:int(limit)] if limit else recipes_all
        serializer = RecipeSerializer(
            recipes, many=True, read_only=True
        )

        return serializer.data

    def get_recipes_count(self, data):
        return data.recipes.count()

    def validate(self, data):
        if self.context.get('request').user == data:
            raise serializers.ValidationError(
                {'errors': 'Нельзя подписаться на себя!'}
            )

        return data


class TagSerializer(serializers.ModelSerializer):
    """Сериализатор Тегов."""

    class Meta:
        model = Tag
        fields = ['id', 'name', 'color', 'slug']
        read_only_fields = ['id', 'name', 'color', 'slug']


class IngredientSerializer(serializers.ModelSerializer):
    """Сериализатор Ингредиентов."""

    class Meta:
        model = Ingredient
        fields = ['id', 'name', 'measurement_unit']
        read_only_fields = ['id', 'name', 'measurement_unit']


class RecipeIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор списка ингредиентов для рецепта при GET запросе."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )
    amount = serializers.ReadOnlyField()

    class Meta:
        model = RecipeIngredient
        fields = [
            'id',
            'name',
            'measurement_unit',
            'amount'
        ]


class RecipeListSerializer(serializers.ModelSerializer):
    """Сериализатор список рецептов при GET запросе."""

    author = UserListSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = RecipeIngredientSerializer(
        many=True, read_only=True, source='ingredient'
    )
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    tags = TagSerializer(many=True, read_only=True)

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
        user = self.context.get('request').user

        if user.is_anonymous or user == data:
            return False

        return user.favorites.filter(recipe=data).exists()

    def get_is_in_shopping_cart(self, data):
        user = self.context.get('request').user

        if user.is_anonymous or user == data:
            return False

        return user.shoppingcart.filter(recipe=data).exists()


class RecipeChoiceIngredientSerializer(serializers.ModelSerializer):
    """Сериализатор выбора ингредиента для создания рецепта."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ['id', 'amount']


class RecipeCreateSerializer(serializers.ModelSerializer):
    """Сериализатор создания, изменения или удаления рецепта."""

    author = UserListSerializer(read_only=True)
    image = Base64ImageField()
    ingredients = RecipeChoiceIngredientSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )

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

    def validate_ingredients(self, ingredients):
        if not ingredients:
            raise serializers.ValidationError(
                {'ingredients': 'Укажите хотябы один игредиент.'},
                code=status.HTTP_400_BAD_REQUEST
            )

        unique_ingredients = set()
        for ingredient in ingredients:
            if not Ingredient.objects.filter(id=ingredient['id']).exists():
                raise serializers.ValidationError(
                    {'ingredients': 'Указан не существующий ингредиент.'},
                    code=status.HTTP_404_NOT_FOUND
                )
            if ingredient['amount'] < 1:
                raise serializers.ValidationError(
                    {'amount': 'Значение должно быть больше 0.'},
                    code=status.HTTP_400_BAD_REQUEST
                )
            unique_ingredients.add(ingredient['id'])

        if len(ingredients) != len(unique_ingredients):
            raise serializers.ValidationError(
                {'ingredients': 'Ингридиенты не должны дублироваться.'},
                code=status.HTTP_400_BAD_REQUEST
            )

        return ingredients

    def validate_tags(self, tags):
        if not tags:
            raise serializers.ValidationError(
                {'tags': 'Укажите хотябы один тег.'},
                code=status.HTTP_400_BAD_REQUEST
            )

        if len(set(tags)) != len(tags):
            raise serializers.ValidationError(
                {'tags': 'Теги не должны дублироваться.'},
                code=status.HTTP_400_BAD_REQUEST
            )

        return tags

    def validate_image(self, image):

        if image is None:
            raise serializers.ValidationError(
                {'image': 'Загрузите картинку вашего рецепта.'},
                code=status.HTTP_400_BAD_REQUEST
            )

        return image

    def validate(self, data):
        fields = [
            'ingredients', 'tags', 'name', 'text', 'image', 'cooking_time'
        ]
        for field in fields:
            if field not in data:
                raise serializers.ValidationError(
                    {f'{field}': f'Укажите {field}.'},
                    code=status.HTTP_400_BAD_REQUEST
                )

        return super().validate(data)

    def set_tags_and_ingredients(self, recipe, tags, ingredients):
        recipe.tags.set(tags)
        RecipeIngredient.objects.bulk_create(
            [RecipeIngredient(
                recipe=recipe,
                ingredient_id=ingredient['id'],
                amount=ingredient['amount']
            ) for ingredient in ingredients]
        )

    def create(self, validated_data):
        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        recipe = Recipe.objects.create(
            author=self.context['request'].user,
            **validated_data
        )
        self.set_tags_and_ingredients(recipe, tags, ingredients)

        return recipe

    def update(self, instance, validated_data):

        tags = validated_data.pop('tags')
        ingredients = validated_data.pop('ingredients')

        RecipeIngredient.objects.filter(
            recipe=instance,
            ingredient__in=instance.ingredients.all()
        )

        self.set_tags_and_ingredients(instance, tags, ingredients)

        instance.save()

        return super().update(instance, validated_data)

    def to_representation(self, value):
        return RecipeListSerializer(value, context=self.context).data
