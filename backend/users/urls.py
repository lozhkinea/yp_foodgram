from django.urls import include, path
from djoser import views
from rest_framework.routers import DefaultRouter

from .views import TokenCreateView, UserViewSet

app_name = 'users'

router = DefaultRouter()
router.register("users", UserViewSet)


urlpatterns = [
    path('', include(router.urls)),
    path('auth/token/login/', TokenCreateView.as_view(), name='login'),
    path(
        'auth/token/logout/', views.TokenDestroyView.as_view(), name='logout'
    ),
]
