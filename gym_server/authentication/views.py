from rest_framework import mixins, viewsets, status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated

from authentication.serializers import RegistrationSerializer, LoginSerializer, RefreshTokenSerializer
from authentication.renderers import UserJSONRenderer
from my_gym.utils import write_refresh_token_to_db


class RegistrationView(mixins.CreateModelMixin,
                       viewsets.GenericViewSet):
    permission_classes = (AllowAny,)
    serializer_class = RegistrationSerializer
    renderer_classes = (UserJSONRenderer,)


class LoginView(mixins.CreateModelMixin,
                viewsets.GenericViewSet):
    permission_classes = (AllowAny,)
    serializer_class = LoginSerializer
    renderer_classes = (UserJSONRenderer,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = serializer.data['id']
        refresh_token = serializer.data['refresh_token']
        write_refresh_token_to_db(user_id, refresh_token)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)


class RefreshTokenView(mixins.CreateModelMixin,
                       viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)
    serializer_class = RefreshTokenSerializer
    renderer_classes = (UserJSONRenderer,)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user_id = serializer.data['id']
        refresh_token = serializer.data['refresh_token']
        write_refresh_token_to_db(user_id, refresh_token)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
