from django.contrib.auth import get_user_model
from django.db.models import Prefetch
from django.shortcuts import get_object_or_404
from djoser import utils, views
from djoser.conf import settings
from rest_framework import serializers, status
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Subscription
from .serializers import SubscriptionSerializer

User = get_user_model()


class TokenCreateView(views.TokenCreateView):
    """
    Use this endpoint to obtain user authentication token.
    """

    def _action(self, serializer):
        token = utils.login_user(self.request, serializer.user)
        token_serializer_class = settings.SERIALIZERS.token
        return Response(
            data=token_serializer_class(token).data,
            status=status.HTTP_201_CREATED,
        )


class UserViewSet(views.UserViewSet):
    @action(
        methods=['post', 'delete'],
        detail=True,  # permission_classes=[IsAdminOrIsSelf],
    )
    def subscribe(self, request, id=None):
        SUBSCRIPTION_NOT_FOUND = {'errors': 'Ошибка: подписка не существует'}
        SELF_SUBSCRIPTION = {'errors': 'Ошибка: подписка на самого себя!'}
        RE_SUBSCRIPTION = {'errors': 'Ошибка: повторная подписка'}
        author = get_object_or_404(User, id=id)
        if request.method == 'POST':
            if author == request.user:
                raise serializers.ValidationError(SELF_SUBSCRIPTION)
            if author.subscribes.filter(user=request.user).exists():
                raise serializers.ValidationError(RE_SUBSCRIPTION)
            author.subscribes.create(user=request.user)
            serializer = SubscriptionSerializer(author)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        if request.method == 'DELETE':
            if not author.subscribes.filter(user=request.user).exists():
                raise serializers.ValidationError(SUBSCRIPTION_NOT_FOUND)
            author.subscribes.filter(user=request.user).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False)
    def subscriptions(self, request):
        subscribes = User.objects.prefetch_related(
            Prefetch(
                'subscribes',
                queryset=Subscription.objects.filter(user=request.user).all(),
            )
        )
        page = self.paginate_queryset(subscribes)
        if page is not None:
            serializer = SubscriptionSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        serializer = SubscriptionSerializer(subscribes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
