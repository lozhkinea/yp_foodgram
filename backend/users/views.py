from django.contrib.auth import get_user_model
from djoser import utils, views
from djoser.conf import settings
from rest_framework import status
from rest_framework.response import Response

settings.LOGIN_FIELD = get_user_model().EMAIL_FIELD


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
