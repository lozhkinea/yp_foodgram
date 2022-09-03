from django.contrib.auth import get_user_model
from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from . import pagination, serializers
from .models import Ingredient, Recipe, Tag

User = get_user_model()


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
    pagination_class = pagination.RecipePagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return serializers.RecipeListSerializer
        else:
            return serializers.RecipeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create(serializer)
        list_serializer = serializers.RecipeListSerializer(
            instance=instance, context={'request': request}
        )
        headers = self.get_success_headers(serializer.data)
        return Response(
            list_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def perform_create(self, serializer):
        return serializer.save(author=self.request.user)

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
            if recipe.favorite.filter(user=request.user).exists():
                raise ValidationError(ALREADY_EXIST)
            recipe.favorite.create(user=request.user)
            serializer = serializers.FavoriteSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not recipe.favorite.filter(user=request.user).exists():
                raise ValidationError(NOT_FOUND)
            recipe.favorite.filter(user=request.user).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        ALREADY_EXIST = {'errors': 'Рецепт уже есть в списке покупок.'}
        NOT_FOUND = {'errors': 'Рецепт в списке покупок не найден.'}
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            if recipe.shopping_cart.filter(user=request.user).exists():
                raise ValidationError(ALREADY_EXIST)
            recipe.shopping_cart.create(user=request.user)
            serializer = serializers.FavoriteSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not recipe.shopping_cart.filter(user=request.user).exists():
                raise ValidationError(NOT_FOUND)
            recipe.shopping_cart.filter(user=request.user).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(permissions.AllowAny,),
    )
    def download_shopping_cart(self, request):
        FILENAME = 'shopping_cart.txt'
        INGREDIENTS = 'user_cart__recipe__recipe_ingredients'
        NAME = f'{INGREDIENTS}__ingredient__name'
        UNIT = f'{INGREDIENTS}__ingredient__measurement_unit'
        ingerdients_in_cart = request.user.annotate(
            weight=Sum(f'{INGREDIENTS}__amount')
        ).values(NAME, 'weight', UNIT)
        text = ''
        for i in ingerdients_in_cart:
            text += f'{i[NAME]} ({i[UNIT]}) - {i["weight"]} \n'.capitalize()
        response = HttpResponse(
            text,
            headers={
                'Content-Type': 'text/plain; charset=UTF-8',
                'Content-Disposition': f'attachment; filename="{FILENAME}"',
            },
        )
        return response
