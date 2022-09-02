from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    email = models.EmailField(_('email address'), max_length=254)
    first_name = models.CharField(_('first name'), max_length=150)
    last_name = models.CharField(_('last name'), max_length=150)

    REQUIRED_FIELDS = ('email', 'first_name', 'last_name')

    class Meta:
        ordering = ('username',)
        verbose_name = _('user')
        verbose_name_plural = _('users')


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribers',
        verbose_name=_('user'),
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='subscribes',
        verbose_name='Автор',
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_subscribe)'
            ),
            models.CheckConstraint(
                check=~models.Q(user=models.F('author')), name='self_subscribe'
            ),
        ]
        ordering = ('user', 'author')
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
