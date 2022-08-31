from django.contrib import admin

from .models import (
    Favorite,
    Ingredient,
    Recipe,
    RecipeIngredient,
    ShoppingCart,
    Tag,
)


class FavotiteAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    search_fields = (
        'user',
        'recipe',
    )
    list_filter = (
        'user',
        'recipe',
    )
    empty_value_display = '-пусто-'


class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'measurement_unit',
        'id',
    )
    search_fields = ('name',)
    list_filter = ('name',)
    empty_value_display = '-пусто-'


class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'author',
        'favorited_count',
        'id',
    )
    search_fields = ('name', 'author')
    list_filter = ('name', 'author', 'tags')
    empty_value_display = '-пусто-'


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = (
        'recipe',
        'ingredient',
        'amount',
        'id',
    )
    empty_value_display = '-пусто-'


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'recipe',
    )
    search_fields = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    empty_value_display = '-пусто-'


class TagAdmin(admin.ModelAdmin):
    list_display = (
        'name',
        'color',
        'slug',
        'id',
    )
    search_fields = ('name', 'color', 'slug')
    list_filter = ('name', 'color', 'slug')
    empty_value_display = '-пусто-'


admin.site.register(Favorite, FavotiteAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
