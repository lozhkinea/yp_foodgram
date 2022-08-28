from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from users.serializers import UserSerializer

from .models import Ingredient, Recipe, RecipesIngredient, Tag

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipesIngredientSerializer(serializers.ModelSerializer):
    # id = serializers.IntegerField(source='ingredient_id')

    class Meta:
        model = RecipesIngredient
        fields = ('id', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    image = Base64ImageField()
    author = UserSerializer()
    ingredients = IngredientSerializer(many=True, read_only=True)
    recipe_to_ingredient = RecipesIngredientSerializer(
        many=True, read_only=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'recipe_to_ingredient',
        )

    def create(self, validated_data):
        print(validated_data)
        ingredients = validated_data.pop('ingredients')
        recipe = super().create(validated_data)
        for ingredient in ingredients:
            print(ingredient)
            current = get_object_or_404(
                Ingredient, id=ingredient['ingredient_id']
            )
            RecipesIngredient.objects.create(
                recipe=recipe, ingredient=current, amount=ingredient['amount']
            )
        return recipe

    def to_representation(self, instance):
        recipe = super().to_representation(instance)
        recipe_to_ingredient = recipe.pop('recipe_to_ingredient')
        for i, ingredient in enumerate(recipe_to_ingredient):
            recipe['ingredients'][i]['amount'] = ingredient['amount']
        return recipe

    def to_internal_value(self, data):
        ret = super().to_internal_value(data)
        print('-' * 80)
        print(ret)
        print('-' * 80)
        return ret


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
