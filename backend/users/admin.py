from django.contrib import admin

from . import models


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


admin.site.register(models.User, UserAdmin)
admin.site.register(models.Subscription, SubscriptionAdmin)
