from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from users.serializers import UserSerializer

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)

User = get_user_model()


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class RecipeIngredientListSerializer(serializers.ModelSerializer):
    class Meta:
        model = RecipeIngredient
        fields = (
            'ingredient',
            'amount',
        )


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = (
            'id',
            'amount',
        )


class RecipeListSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    image = serializers.ImageField()
    author = UserSerializer()
    ingredients = IngredientSerializer(many=True, read_only=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()
    recipe_ingredients = RecipeIngredientSerializer(many=True, read_only=True)

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',
            'recipe_ingredients',
        )

    def get_is_favorited(self, recipe):
        return Favorite.objects.filter(
            user=self.context['request'].user, recipe=recipe
        ).exists()

    def get_is_in_shopping_cart(self, recipe):
        return ShoppingCart.objects.filter(
            user=self.context['request'].user, recipe=recipe
        ).exists()

    def to_representation(self, instance):
        recipe = super().to_representation(instance)
        recipe_ingredients = recipe.pop('recipe_ingredients')
        d = {item['ingredient']: item['amount'] for item in recipe_ingredients}
        for i, ingredient in enumerate(recipe['ingredients']):
            recipe['ingredients'][i]['amount'] = d[ingredient['id']]
        return recipe


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        print('3 =-=-=-=', validated_data)
        recipe = super().create(validated_data)
        for item in ingredients:
            current = get_object_or_404(Ingredient, id=item['ingredient'].id)
            RecipeIngredient.objects.create(
                recipe=recipe, ingredient=current, amount=item['amount']
            )
        return recipe

    def to_representation(self, instance):
        print('to_representation in')
        fields = self._readable_fields
        for field in fields:
            print('---', field)
        recipe = super().to_representation(instance)
        print('to_representation out')
        return recipe


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
