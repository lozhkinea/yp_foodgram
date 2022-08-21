from django.contrib import admin

from .models import Favotites, Ingredient, Recipe, ShoppingCart, Subscribe, Tag

admin.site.register(Favotites)
admin.site.register(Ingredient)
admin.site.register(Recipe)
admin.site.register(ShoppingCart)
admin.site.register(Subscribe)
admin.site.register(Tag)
