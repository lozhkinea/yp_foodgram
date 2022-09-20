from rest_framework.routers import DefaultRouter

from . import views

app_name = 'recipes'

router = DefaultRouter()
router.register('ingredients', views.IngredientViewSet)
router.register('recipes', views.RecipeViewSet, basename='recipe')
router.register('tags', views.TagViewSet)

urlpatterns = router.urls
