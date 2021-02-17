import jwt

from django.conf import settings

from rest_framework import exceptions, authentication
from rest_framework.authentication import TokenAuthentication

from .models import UserModel


class TokenAuth(TokenAuthentication):
    model = UserModel
    authentication_header_prefix = 'Token'

    def authenticate(self, request):

        request.user = None

        auth_header = authentication.get_authorization_header(request).split()
        auth_header_prefix = self.authentication_header_prefix.lower()

        if not auth_header:
            return None

        if len(auth_header) == 1:
            return None

        elif len(auth_header) > 2:
            return None

        prefix = auth_header[0].decode('utf-8')
        token = auth_header[1].decode('utf-8')

        if prefix.lower() != auth_header_prefix:
            return None

        return self.authenticate_credentials(token)

    def authenticate_credentials(self, token):
        model = self.get_model()

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
        except jwt.ExpiredSignatureError:
            msg = 'Ошибка аутентификации. Истек срок действия токена.'
            raise exceptions.AuthenticationFailed(msg.encode('utf-8'))
        except Exception as e:
            msg = 'Ошибка аутентификации. Невозможно декодировать токен.'
            raise exceptions.AuthenticationFailed(msg.encode('utf-8'))

        try:
            user = model.objects.get(pk=payload['id'])
        except model.DoesNotExist:
            msg = 'Пользователь соответствующий данному токену не найден.'
            raise exceptions.AuthenticationFailed(msg.encode('utf-8'))

        if not user.is_active:
            msg = 'Данный пользователь деактивирован.'
            raise exceptions.AuthenticationFailed(msg.encode('utf-8'))

        return (user, token)
