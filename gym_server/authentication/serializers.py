import jwt

from rest_framework import serializers, exceptions

from django.contrib.auth.hashers import check_password
from django.conf import settings

from my_gym.models import UserModel, TokenModel


class RegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(
        max_length=128,
        min_length=8,
        write_only=True
    )

    token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = UserModel
        fields = ('id', 'first_name', 'last_name', 'email', 'role', 'password', 'token')


class LoginSerializer(serializers.ModelSerializer):
    email = serializers.CharField(max_length=255)
    password = serializers.CharField(max_length=128, write_only=True)
    access_token = serializers.CharField(max_length=255, read_only=True)
    refresh_token = serializers.CharField(max_length=255, read_only=True)

    class Meta:
        model = UserModel
        fields = ('id', 'email', 'password', 'access_token', 'refresh_token')
        read_only_fields = ('access_token', 'refresh_token')

    def validate(self, data):
        email = data.get('email', None)
        password = data.get('password', None)

        if email is None:
            raise serializers.ValidationError(
                'Email address is required to log in.'
            )
        if password is None:
            raise serializers.ValidationError(
                'Password is required to log in.'
            )
        try:
            user = UserModel.objects.get(email=email)
        except UserModel.DoesNotExist:
            raise serializers.ValidationError(
                'User with given email does not exist.'
            )

        if not check_password(password, user.password):
            raise serializers.ValidationError(
                'Wrong password.'
            )
        if not user.is_active:
            raise serializers.ValidationError(
                'This user has been deactivated.'
            )

        return {
            'id': user.id,
            'email': user.email,
            'role': user.role,
            'access_token': user.access_token,
            'refresh_token': user.refresh_token
        }

class RefreshTokenSerializer(serializers.ModelSerializer):
    refresh_token = serializers.CharField(max_length=255)

    class Meta:
        model = UserModel
        fields = ('id', 'email', 'access_token', 'refresh_token')
        read_only_fields = ('email',)

    def validate(self, data):
        token = data.get('refresh_token')

        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms="HS256")
        except jwt.ExpiredSignatureError:
            msg = 'Ошибка аутентификации. Истек срок действия токена.'
            raise exceptions.AuthenticationFailed(msg.encode('utf-8'))
        except Exception as e:
            msg = 'Ошибка аутентификации. Невозможно декодировать токен.'
            raise exceptions.AuthenticationFailed(msg.encode('utf-8'))

        try:
            user = UserModel.objects.get(pk=payload['id'])
        except UserModel.DoesNotExist:
            msg = 'Пользователь соответствующий данному токену не найден.'
            raise exceptions.AuthenticationFailed(msg.encode('utf-8'))

        if not user.is_active:
            msg = 'Данный пользователь деактивирован.'
            raise exceptions.AuthenticationFailed(msg.encode('utf-8'))

        is_refresh = payload.get('refresh', None)

        if is_refresh is None:
            msg = 'Неверный токен. Необходим REFRESH TOKEN.'
            raise exceptions.ValidationError(msg.encode('utf-8'))
        else:
            return {
            'id': user.id,
            'email': user.email,
            'role': user.role,
            'access_token': user.access_token,
            'refresh_token': user.refresh_token
        }