from django.urls import include, path

from djoser import views
from .views import CustomTokenCreateView

app_name = 'users'


urlpatterns = [
    path('', include('djoser.urls')),
    path('auth/token/login/', CustomTokenCreateView.as_view(), name='login'),
    path(
        'auth/token/logout/', views.TokenDestroyView.as_view(), name='logout'
    ),
]
