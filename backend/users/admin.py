from django.contrib import admin
from django.contrib.auth import get_user_model

from .models import Subscription

User = get_user_model()


class UserAdmin(admin.ModelAdmin):
    list_display = (
        'username',
        'first_name',
        'last_name',
        'email',
        'is_superuser',
        'id',
    )
    list_filter = ('username', 'email')


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author', 'id')
    list_filter = ('user', 'author')


admin.site.register(User, UserAdmin)
admin.site.register(Subscription, SubscriptionAdmin)
