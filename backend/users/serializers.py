from djoser import serializers as ds
from rest_framework import serializers

from recipes.models import Recipe

from .models import Subscription, User


class UserCreateSerializer(ds.UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class UserSerializer(ds.UserSerializer):
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
        )

    def get_is_subscribed(self, obj):
        return (
            (user := self.context['request'].user)
            and user.is_authenticated
            and Subscription.objects.filter(user=user, author=obj).exists()
        )


class SubscriptionRecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class SubscriptionSerializer(UserSerializer):
    recipes = SubscriptionRecipeSerializer(many=True, read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = UserSerializer.Meta.model
        fields = UserSerializer.Meta.fields + ('recipes', 'recipes_count')

    def get_recipes_count(self, user):
        return user.recipes.count()
