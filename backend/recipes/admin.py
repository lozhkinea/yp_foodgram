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
    list_display = ('recipe', 'user', 'id')
    list_filter = ('recipe', 'user')


class IngredientAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit', 'id')
    list_filter = ('name',)


class RecipeAdmin(admin.ModelAdmin):
    list_display = ('name', 'author', 'favorited_count', 'id')
    list_filter = ('name', 'author')


class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('ingredient', 'amount', 'recipe', 'id')
    list_filter = ('recipe',)


class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('recipe', 'user', 'id')
    list_filter = ('recipe', 'user')


class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'color', 'slug', 'id')
    list_filter = ('name', 'color', 'slug')


admin.site.register(Favorite, FavotiteAdmin)
admin.site.register(Ingredient, IngredientAdmin)
admin.site.register(Recipe, RecipeAdmin)
admin.site.register(RecipeIngredient, RecipeIngredientAdmin)
admin.site.register(ShoppingCart, ShoppingCartAdmin)
admin.site.register(Tag, TagAdmin)
