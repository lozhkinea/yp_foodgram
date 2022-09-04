from django.db.models import Count
from django_filters import CharFilter, FilterSet, ModelChoiceFilter

from recipes.models import Favorite, Recipe


class RecipeFilter(FilterSet):
    tags = CharFilter(field_name='tags', lookup_expr='slug')

    class Meta:
        model = Recipe
        fields = ('author', 'tags')
