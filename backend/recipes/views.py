from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions
from rest_framework import serializers as drf_slzrs
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from . import serializers
from .models import Ingredient, Recipe, Tag


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    pagination_class = None
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    serializer_class = serializers.RecipeSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request, pk=None):
        ALREADY_EXIST = {'errors': 'Рецепт уже есть в избранном.'}
        NOT_FOUND = {'errors': 'Рецепт в избранном не найден.'}
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            if recipe.fav_recipe_to_user.filter(user=request.user).exists():
                raise drf_slzrs.ValidationError(ALREADY_EXIST)
            recipe.fav_recipe_to_user.create(user=request.user)
            serializer = serializers.FavoriteSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not recipe.fav_recipe_to_user.filter(
                user=request.user
            ).exists():
                raise drf_slzrs.ValidationError(NOT_FOUND)
            recipe.fav_recipe_to_user.filter(user=request.user).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
