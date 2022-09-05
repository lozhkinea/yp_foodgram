from django_filters import CharFilter, FilterSet

from recipes.models import Recipe


class RecipeFilter(FilterSet):
    tags = CharFilter(field_name='tags', lookup_expr='slug')

    class Meta:
        model = Recipe
        fields = ('author', 'tags')
