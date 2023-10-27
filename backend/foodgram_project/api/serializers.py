from rest_framework import serializers

from recipes.models import Ingredient, Tag, Recipe, Follow


class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        field = '__all__'


class FollowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        field = '__all__'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        field = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        field = '__all__'
