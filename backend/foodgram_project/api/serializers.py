from rest_framework import serializers

from recipes.models import Ingredient, Tag, Recipe
from users.models import Follow, User


class UserListSerializer(serializers.ModelSerializer):
    """
    Сериализатор пользователей. GET.
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

    def get_is_subscribed(self, obj: User) -> bool:
        user = self.context['request'].user

        if user.is_anonymous or user == obj:
            return False

        return user.follower.filter(author=obj).exists()


class UserCreateSerializer(serializers.ModelSerializer):
    """
    Сериализатор создания пользователя. POST.
    """
    class Meta:
        model = User
        fields = [
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

    def create(self, validated_data) -> User:
        user = User(
            validated_data['email'],
            validated_data['username'],
            validated_data['first_name'],
            validated_data['last_name']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = '__all__'


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'
        read_only_fields = ['__all__',]


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'
        read_only_fields = ['__all__',]
