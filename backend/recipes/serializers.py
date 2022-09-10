from rest_framework import serializers
from users.serializers import UserSerializer

from .fields import Base64ImageField
from .models import (Favorite, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Tag)

IS_FAVORITED = 'is_favorited'
IS_IN_SHOPPING_CART = 'is_in_shopping_cart'


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = "__all__"


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = "__all__"


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        source='ingredient', queryset=Ingredient.objects.all()
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


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
            IS_FAVORITED,
            IS_IN_SHOPPING_CART,
            'name',
            'image',
            'text',
            'cooking_time',
            'recipe_ingredients',
        )

    def get_is_favorited(self, recipe):
        return (
            (user := self.context['request'].user)
            and user.is_authenticated
            and Favorite.objects.filter(user=user, recipe=recipe).exists()
        )

    def get_is_in_shopping_cart(self, recipe):
        return (
            (user := self.context['request'].user)
            and user.is_authenticated
            and ShoppingCart.objects.filter(user=user, recipe=recipe).exists()
        )

    def to_representation(self, instance):
        recipe = super().to_representation(instance)
        recipe_ingredients = recipe.pop('recipe_ingredients')
        amounts = {item['id']: item['amount'] for item in recipe_ingredients}
        for i, ingredient in enumerate(recipe['ingredients']):
            recipe['ingredients'][i]['amount'] = amounts[ingredient['id']]
        return recipe


class RecipeSerializer(serializers.ModelSerializer):
    ingredients = RecipeIngredientSerializer(many=True, write_only=True)
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

    def validate(self, data):
        values = [item['ingredient'].id for item in data['ingredients']]
        if len(values) != len(set(values)):
            raise serializers.ValidationError(
                {'errors': 'Ингредиенты не должны повторяться'}
            )
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')
