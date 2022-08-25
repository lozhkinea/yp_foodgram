from django.urls import include, path
from rest_framework.routers import SimpleRouter

from . import views

app_name = 'recipes'

router = SimpleRouter()
router.register('ingredients', views.IngredientViewSet)
router.register('recipes', views.RecipeViewSet)
router.register('tags', views.TagViewSet)


urlpatterns = [
    path('', include(router.urls)),
]
