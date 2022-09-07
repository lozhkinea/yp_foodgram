from django.shortcuts import get_object_or_404
from djoser import views
from rest_framework import permissions, serializers, status
from rest_framework.decorators import action
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from .models import User
from .serializers import SubscriptionSerializer


class TokenCreateView(views.TokenCreateView):
    def _action(self, serializer):
        response = super()._action(serializer)
        response.status_code = status.HTTP_201_CREATED
        return response


class UserViewSet(views.UserViewSet):
    pagination_class = LimitOffsetPagination
    permission_classes = (permissions.IsAuthenticated,)

    @action(methods=['post', 'delete'], detail=True)
    def subscribe(self, request, id):
        author = get_object_or_404(User, id=id)
        queryset = author.subscribes.filter(user=request.user)
        match request.method:
            case 'POST':
                if author == request.user:
                    raise serializers.ValidationError(
                        {'errors': 'Подписка на самого себя.'}
                    )
                if queryset.exists():
                    raise serializers.ValidationError(
                        {'errors': 'Подписка уже существует.'}
                    )
                author.subscribes.create(user=request.user)
                serializer = SubscriptionSerializer(author)
                return Response(
                    serializer.data, status=status.HTTP_201_CREATED
                )
            case 'DELETE':
                if not queryset.exists():
                    raise serializers.ValidationError(
                        {'errors': 'Подписка не найдена.'}
                    )
                queryset.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)

    @action(methods=['get'], detail=False)
    def subscriptions(self, request):
        subscribes = User.objects.filter(subscribes__user=request.user).all()
        page = self.paginate_queryset(subscribes)
        serializer = SubscriptionSerializer(page, many=True)
        recipes_limit = request.query_params.get('recipes_limit')
        if recipes_limit is not None:
            recipes_limit = int(recipes_limit)
            for i, item in enumerate(serializer.data):
                serializer.data[i]['recipes'] = item['recipes'][:recipes_limit]
        return self.get_paginated_response(serializer.data)
