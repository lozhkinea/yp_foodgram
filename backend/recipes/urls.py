from django.conf import settings
from django.conf.urls.static import static
from rest_framework.routers import SimpleRouter

from . import views

app_name = 'recipes'

router = SimpleRouter()
router.register('ingredients', views.IngredientViewSet)
router.register('recipes', views.RecipeViewSet)
router.register('tags', views.TagViewSet)

urlpatterns = router.urls

if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )
