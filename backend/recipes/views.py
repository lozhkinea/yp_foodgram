from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response
from rest_framework.serializers import ValidationError

from . import serializers
from .filters import RecipeFilter
from .models import Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag
from .permissions import IsAdminOrReadOnly, IsOwnerOrAdminOrReadOnly


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializer
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = serializers.IngredientSerializer
    pagination_class = None
    permission_classes = (IsAdminOrReadOnly,)
    filter_backends = (filters.SearchFilter,)
    search_fields = ('^name',)


class RecipeViewSet(viewsets.ModelViewSet):
    pagination_class = LimitOffsetPagination
    permission_classes = (IsOwnerOrAdminOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def _get_filtered_queryset(self, qs, key):
        match key:
            case 'is_favorited':
                return qs.filter(favorite__user=self.request.user)
            case 'is_in_shopping_cart':
                return qs.filter(shopping_cart__user=self.request.user)

    def get_queryset(self):
        queryset = Recipe.objects.all()
        for key in ('is_favorited', 'is_in_shopping_cart'):
            if self.request.query_params.get(key):
                if not self.request.user.is_authenticated:
                    return Recipe.objects.none()
                queryset = self._get_filtered_queryset(queryset, key)
        return queryset

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return serializers.RecipeListSerializer
        else:
            return serializers.RecipeSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.perform_create_update(serializer)
        headers = self.get_success_headers(serializer.data)
        list_serializer = serializers.RecipeListSerializer(
            instance=instance, context={'request': request}
        )
        return Response(
            list_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers,
        )

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(
            instance, data=request.data, partial=partial
        )
        serializer.is_valid(raise_exception=True)
        self.perform_create_update(serializer)
        list_serializer = serializers.RecipeListSerializer(
            instance=instance, context={'request': request}
        )
        return Response(list_serializer.data)

    def perform_create_update(self, serializer):
        serializer.validated_data['author'] = self.request.user
        ingredients = serializer.validated_data.pop('ingredients')
        match self.request.method:
            case 'POST':
                serializer.instance = serializer.create(
                    serializer.validated_data
                )
            case 'PUT':
                serializer.update(
                    serializer.instance, serializer.validated_data
                )
                serializer.instance.recipe_ingredients.all().delete()
        for item in ingredients:
            ingredient = get_object_or_404(
                Ingredient, id=item['ingredient'].id
            )
            RecipeIngredient.objects.create(
                recipe=serializer.instance,
                ingredient=ingredient,
                amount=item['amount'],
            )
        return serializer.instance

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        queryset = recipe.favorite.filter(user=request.user)
        match request.method:
            case 'POST':
                if queryset.exists():
                    raise ValidationError(
                        {'errors': 'Рецепт уже есть в избранном.'}
                    )
                recipe.favorite.create(user=request.user)
                serializer = serializers.FavoriteSerializer(recipe)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            case 'DELETE':
                if not queryset.exists():
                    raise ValidationError(
                        {'errors': 'Рецепт в избранном не найден.'}
                    )
                queryset.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['post', 'delete'],
        detail=True,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        queryset = recipe.shopping_cart.filter(user=request.user)
        if request.method == 'POST':
            if queryset.exists():
                raise ValidationError(
                    {'errors': 'Рецепт уже есть в списке покупок.'}
                )
            recipe.shopping_cart.create(user=request.user)
            serializer = serializers.FavoriteSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not queryset.exists():
                raise ValidationError(
                    {'errors': 'Рецепт в списке покупок не найден.'}
                )
            queryset.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        methods=['get'],
        detail=False,
        permission_classes=(permissions.IsAuthenticated,),
    )
    def download_shopping_cart(self, request):
        FILENAME = 'shopping_cart.txt'
        NAME = 'recipe__recipe_ingredients__ingredient__name'
        UNIT = 'recipe__recipe_ingredients__ingredient__measurement_unit'
        AMOUNT = 'recipe__recipe_ingredients__amount'
        ingerdients_in_cart = (
            ShoppingCart.objects.filter(user=request.user)
            .values(NAME)
            .annotate(weight=Sum(AMOUNT))
            .values(NAME, 'weight', UNIT)
        )
        text = 'Список покупок:\n'
        for i in ingerdients_in_cart:
            text += f'{i[NAME]} ({i[UNIT]}) - {i["weight"]} \n'.capitalize()
        print(text)
        response = HttpResponse(
            text,
            headers={
                'Content-Type': 'text/plain; charset=UTF-8',
                'Content-Disposition': f'attachment; filename="{FILENAME}"',
            },
        )
        return response
